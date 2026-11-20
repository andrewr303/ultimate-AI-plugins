# GEO research evidence

What published research does and does not show about generative engine optimization, with exact numbers, study types and caveats, plus the claims commonly repeated without evidence. Skills use this file whenever a report mentions research. Method for measuring a real site is in [measurement-protocol.md](measurement-protocol.md); editorial practice is in [citability-and-rewrite.md](citability-and-rewrite.md).

As of 2026-11-01. Facts cite [current-facts.md](current-facts.md). Studies are quoted from their own abstracts and tables as recorded in the 2026-11-01 research pass.

## Study-type labels

Label every study by type in every report.

| Label | Meaning | How to write about it |
| --- | --- | --- |
| P | Peer-reviewed paper (venue stated) | Quote numbers with the setup and caveats |
| PP | Preprint, not peer reviewed | Say "preprint" every time |
| IR | Independent research organization, not peer reviewed | Say who ran it, when and on what sample |
| Vendor study | Research published by an SEO or analytics vendor | "Vendor study, not verified"; never causal |
| Project self-report | A tool's own published evaluation | Name the project and say it is self-reported |
| V | Vendor documentation about its own product | Current statement of that product; see the fact registry |

## The GEO paper

Aggarwal, Murahari, Rajpurohit, Kalyan, Narasimhan and Deshpande, "GEO: Generative Engine Optimization", KDD 2024 (P), DOI 10.1145/3637528.3671900, arXiv:2311.09735 v3 (2024-06-28) ([F-AI-31](current-facts.md#f-ai-31)).

**Setup.** GEO-bench: 10,000 queries from 9 sources across 25 domains, split 8,000 / 1,000 / 1,000. A simulated generative engine took the top 5 Google results for each query and generated an answer with gpt-3.5-turbo. For each method, one randomly chosen source was rewritten by an LLM. Metrics: Position-Adjusted Word Count (PAWC, how much of the answer comes from the source, weighted by position) and a G-Eval "Subjective Impression" score; 5 seeds.

**Table 1, test split** (absolute scores; baseline 19.3 on both metrics; relative change computed from the table):

| Method | PAWC | Change vs 19.3 | Subjective Impression | Change vs 19.3 |
| --- | --- | --- | --- | --- |
| Quotation Addition | 27.2 | +41% | 24.7 | +28% |
| Statistics Addition | 25.2 | +31% | 23.7 | +23% |
| Fluency Optimization | 24.7 | +28% | 21.9 | +13% |
| Cite Sources | 24.6 | +27% | 21.9 | +13% |
| Technical Terms | 22.7 | +18% | 21.4 | +11% |
| Easy-to-Understand | 22.0 | +14% | 20.5 | +6% |
| Authoritative | 21.3 | +10% | 22.9 | +19% |
| Unique Words | 20.5 | +6% | 20.4 | +6% |
| Keyword Stuffing | 17.7 | −8% | 20.2 | +5% |

The paper's text summarizes the top methods as "30-40%" on PAWC and "15-30%" on Subjective Impression.

**Rank effect (Table 2).** Gains concentrate on lower-ranked sources. Cite Sources: −30.3% for the rank-1 source, +115.1% for the rank-5 source. Quotation Addition rank 5: +99.7%. Statistics Addition rank 5: +97.9%.

**Domain effects (Table 3).** Authoritative phrasing worked best for debate and history; Cite Sources for statements, facts and law; Quotation for people and society, explanation and history; Statistics for law and government, debate and opinion.

**Combinations (Figure 4, 200-example subset).** Fluency Optimization plus Statistics Addition was best, more than 5.5% above any single method.

**Perplexity.ai (Table 5).** Baseline PAWC 24.1 and Subjective Impression 24.7; Quotation 29.1 / 32.1; Statistics 26.2 / 33.9; Keyword Stuffing 21.9 / 28.1. The abstract reports gains of up to 37% on Perplexity.

Table 2, 3, 5 and Figure 4 details and the setup: [F-AI-53](current-facts.md#f-ai-53) (same paper as [F-AI-31](current-facts.md#f-ai-31)).

**Caveats that must travel with these numbers:**

1. The gains are for a source that is already in a fixed retrieved context. The paper does not measure being crawled, retrieved, ranked or clicked.
2. Gains concentrate on lower-ranked sources; the top source can lose.
3. A later benchmark found most such methods largely ineffective in practice (next section).
4. "Statistics Addition" and "Quotation Addition" mean adding real statistics and quotations. Inventing them is fabrication, whatever the lab score.
5. The numbers come from one simulated engine built on gpt-3.5-turbo in 2023 and 2024.

Misattributions to avoid: per-institution splits ("Princeton found 40%", "IIT Delhi found 115%"), a "2.1x definition effect" and "30-115% more visibility" are not findings of this paper. The 115% figure is Cite Sources for the rank-5 source only.

## C-SEO Bench

Puerto et al., C-SEO Bench, arXiv:2506.11097 v3 (2025-10-20), NeurIPS 2025 Datasets and Benchmarks track (P) ([F-AI-32](current-facts.md#f-ai-32)). Across question answering and product recommendation in three domains each, most conversational-SEO methods were largely ineffective and often hurt ranking; traditional SEO that improves a source's rank in the model's context was more effective; and gains shrank as more sites adopted the same methods, because the setting is congested and zero-sum.

## Preprints

| Study | Type | Finding | Caveat |
| --- | --- | --- | --- |
| Chen, Wang, Chen and Koudas, "Generative Engine Optimization: How to Dominate AI Search", arXiv:2509.08919 (2025-09-10) | PP | AI search showed a systematic bias toward earned media (third-party sources) compared with Google's more balanced mix; engines differed in domain diversity, freshness, cross-language stability and phrasing sensitivity | A "90% of AI visibility from earned media" figure circulating in trade press is not in the abstract |
| Wu, Zhong, Kim and Xiong, AutoGEO, arXiv:2510.11438 (2025-10-13) | PP, venue unknown | Learns engine preference rules with LLMs and rewrites content | A 2026 preprint (FeatGEO, arXiv:2604.19113, seen only as a snippet) reports AutoGEO below baseline in its setup |
| Martinez, critical survey of 45 studies (November 2023 to July 2026), arXiv:2607.14035 (2026-07-15) | PP, single author | Topical relevance and context position are the most reproducible levers; generic heuristics transfer poorly; citation-oriented rewrites can impair retrieval; no reviewed technique shows a stable, longitudinal, cross-platform causal effect on organic discoverability | A survey, not new experiments |
| E-GEO, arXiv:2511.20867 (as described by eGEOagents) | PP, needs verification | An e-commerce product-description re-ranking testbed with an LLM re-ranker | Not evidence about ChatGPT, Perplexity or Gemini citations of web pages |

Sources and labels for the table: [F-AI-54](current-facts.md#f-ai-54), [F-AI-55](current-facts.md#f-ai-55) and [F-AI-56](current-facts.md#f-ai-56) (all PP); the FeatGEO result and E-GEO were not re-read and have no registry ID.

## Independent research on clicks

Pew Research Center (IR, 2025-07-22): in March 2025 browsing data from 900 US adults (68,879 Google searches), users clicked a result in 8% of visits that showed an AI summary versus 15% without one, and clicked a link inside the summary in 1% of visits; 18% of searches showed a summary ([F-AI-33](current-facts.md#f-ai-33); sample details [F-AI-57](current-facts.md#f-ai-57)). Google disputed the methodology (third-party report). Use it as context for click loss, never as a forecast for one site.

## Tool self-reports

- eGEOagents (MIT) pre-registered a validation of its LLM "would an engine cite this?" judge against real Perplexity citations and failed its own 0.65 mean-AUC gate in every run: 0.649 (0.627 on a re-run of the same data), 0.637 and 0.559 (project self-report, https://github.com/mverab/eGEOagents, `eval/jev_selection/README.md`).
- The same project's published before and after runs (2026-10-04) show whole-page LLM rewrites shrinking long pages by about a third and dropping dates, primary-source links and data points while its keyword score rose (`docs/examples.md` in the same repository).

Lesson: an unvalidated score, including this plugin's citability heuristic, is a proxy. Validate it with the method in [measurement-protocol.md](measurement-protocol.md#validating-a-rubric) before treating it as predictive.

## Vendor studies

Citation-share, click-through and correlation studies from SEO and analytics vendors (for example Ahrefs, Semrush, Profound, BrightEdge, SE Ranking, OtterlyAI, Search Influence) were not verified in the research pass. They are marketing research: label them "vendor study", give the publisher and date, state the sample and metric, and never present them as causal or as current for a specific site.

## Claims you will hear

| Claim | Status as of 2026-11-01 | What to say instead |
| --- | --- | --- |
| "Passages of 134 to 167 words get cited most" | Unverified third-party analysis | A house heuristic band only ([citability-and-rewrite.md](citability-and-rewrite.md#passage-heuristics)) |
| "llms.txt increases AI citations or Google rankings" | No evidence; Google Search ignores llms.txt ([F-AI-11](current-facts.md#f-ai-11)) | Optional for agents and developer tools ([agent-readiness.md](agent-readiness.md#honest-framing)) |
| "Adding statistics raises visibility by 40%" | Lab result for an already-retrieved source, mostly lower-ranked ones ([F-AI-31](current-facts.md#f-ai-31)); replication weak ([F-AI-32](current-facts.md#f-ai-32)) | Real, sourced statistics can help readers; no promise of citations |
| "Brand mentions matter three times more than backlinks for AI" | Vendor correlation, coefficients unverified | Earned coverage plausibly matters (preprint evidence above); measure your own surfaces |
| "Most AI Overview citations come from top-10 pages" | Vendor study, unverified | AI features use indexed, snippet-eligible pages ([F-AI-11](current-facts.md#f-ai-11)) |
| "Wikipedia is nearly half of ChatGPT citations" | Misread vendor figure (share among top cited domains), time-sensitive | Record cited domains in your own panel |
| "FAQ or special schema helps AI answers" | Google lists over-focus on structured data and special markup among misconceptions ([F-AI-12](current-facts.md#f-ai-12)) | Structured data must match visible content and serves rich-result eligibility |
| "Chunk pages into small blocks for AI" | Listed by Google as a misconception ([F-AI-12](current-facts.md#f-ai-12)) | Clear sections that also serve readers |
| "AI crawlers never run JavaScript" | Not documented by the vendors | Server-render primary content as the safe default ([seo-rendering](../skills/seo-rendering/SKILL.md)) |
| "GEO results appear within minutes" | Only the citability proxy is fast; surfacing takes days to weeks | Use the four-layer model ([measurement-protocol.md](measurement-protocol.md#four-layers)) |

## Google's misconception list

Google's generative-AI optimization guide (published 2026-05-15) says optimizing for generative AI search is still SEO and names as misconceptions: llms.txt or special AI files and markup, chunking content, rewriting content for AI or for long-tail variants, inauthentic mentions, over-focus on structured data, and "AEO/GEO hacks"; it adds that mass-producing pages for query variants primarily to manipulate rankings or AI responses may be scaled content abuse ([F-AI-12](current-facts.md#f-ai-12)). Google's spam policies treat manipulating generative AI responses as spam ([F-T-32](current-facts.md#f-t-32)).

## How to cite in reports

1. Name the study, its type label, venue or publisher and date.
2. Give the setup in one clause ("fixed retrieved context, simulated engine").
3. Quote the exact number with its baseline ("PAWC 27.2 vs 19.3, +41%"), never a rounded headline.
4. Add the caveat that limits it ("gains concentrate on lower-ranked sources; replication found most methods ineffective").
5. Never turn a correlation or a lab effect into a forecast or a guarantee for the user's site.
6. Prefer the site's own measurements over any study; say "not measured" when there are none.

## Needs verification

- FeatGEO and AgentGEO abstracts (seen only as snippets).
- E-GEO preprint title, authorship and setup.
- Any vendor statistic before quoting it.
- Google's response to the Pew study (third-party report).
