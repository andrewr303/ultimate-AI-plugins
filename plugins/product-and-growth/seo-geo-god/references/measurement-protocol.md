<!-- Portions adapted from aaron-marketing-skills (Apache-2.0, Copyright 2024 Aaron He Zhu). Modified for SEO-GEO-god on 2026-11-01: four-layer latency model, controls, read-back windows and decision vocabulary rewritten in our own words, merged with MIT-licensed observation-state, collector and validation rules, and bound to the bundled ledger, data sources and fact IDs. See NOTICE.md. -->
# Measurement protocol

How to tell whether search and AI-answer visibility changed, and whether a specific change plausibly caused it: the four measurement layers and their latency, prompt-panel design, observation states, hold-outs and controls, read-back windows, decisions, statistics, data sources, the local ledger, the collector contract and how to validate any scoring rubric against real citations. This is the reference behind [seo-geo-measurement](../skills/seo-geo-measurement/SKILL.md). One-off historical analysis of exports belongs to [search-data-analysis](../skills/search-data-analysis/SKILL.md).

As of 2026-11-01. Facts cite [current-facts.md](current-facts.md). Numbers marked "heuristic" are ours.

## Four layers

SEO and GEO outcomes arrive late and are confounded: a number moves because of the change, because the engine changed, because a competitor published, or because of the season. Separate the fast proxies from the slow outcomes, label which is which, and attribute slow outcomes only against a control.

| Layer | Question | Typical latency | Kind | How to observe |
| --- | --- | --- | --- | --- |
| 1. Crawler access | Can the relevant bots fetch and parse the page? | Immediate | Precondition | `SG robots`, `SG access-check --live`, server logs (`SG referrers access.log --log --bots`), rendered HTML checks |
| 2. Citability | Given retrieval, is the passage easy to quote accurately? | Minutes | Proxy | `SG citability`, `SG content-lint`, an explicit-URL test in a live-fetch assistant (only if logs show the fetch happened) |
| 3. AI surfacing | Is the page cited for the bare query, unprompted? | Days to weeks | Outcome (GEO) | Prompt panel without the URL, repeated over time, against a control |
| 4. Rankings and clicks | Position, impressions, clicks, AI referrals | Weeks to months | Outcome (SEO) | Search Console, Bing Webmaster Tools, GA4 and log exports, against a control |

Rules:

- Never read a missing citation (layer 3) as "the content is bad" until layer 1 shows the relevant crawler received a 200 with the content in the HTML. "Not fetched yet" and "fetched but not chosen" look the same in an answer.
- A layer 2 improvement is necessary, not sufficient, for layer 3. Never present a proxy as an outcome.
- User-triggered fetchers can reach a page the indexer is blocked from ([F-AI-05](current-facts.md#f-ai-05)), so an explicit-URL test can succeed while unprompted surfacing stays impossible. Test access per token.
- No AI surface offers a "recrawl now" button. Layers 3 and 4 are as slow as SEO.

## Panel design

A prompt panel is a frozen set of queries run against named surfaces on a fixed schedule. Use [prompt-panel.example.csv](../templates/prompt-panel.example.csv) as the starting file.

- **Freeze the queries before the baseline.** Queries come from the user, Search Console exports or a tracker export, not from the agent's imagination. Changing the set mid-test restarts the test.
- **Mix the classes.** Include branded queries, generic category queries (`commercial`), technical and how-to queries (`informational` with a `technical` or `how-to` intent) and comparison queries (`commercial` with a `comparison` intent). Class names match the project contract (`branded`, `generic`, `commercial`, `informational`, `navigational`, `other`).
- **Size.** 10 to 50 queries per page group (heuristic). Small panels give wide intervals; say so.
- **Hold out about a fifth of the queries.** Mark them `holdout=true`; they are never used to choose or tune rewrites, so they show whether improvements generalize.
- **One surface per column of evidence.** Measure Google AI Overviews, Google AI Mode, the Gemini app, ChatGPT search, Perplexity, Copilot and Claude separately. Surface IDs used in this plugin: `google-ai-overviews`, `google-ai-mode`, `gemini-app`, `chatgpt-search`, `perplexity`, `copilot`, `claude`. Report only surfaces actually sampled; all others are "not measured".
- **Fixed conditions.** Same locale, region, language, device, logged-in state and search or retrieval mode for every sample; a fresh session per sample; record the model label when the surface shows one.
- **Repeat samples.** Answers vary between runs. Sample each query several times per surface per read (5 is our heuristic) and record rates, not single yes or no answers.
- **Record per sample:** surface, query, query class, hold-out flag, status, cited URLs, the cited statement (at most 300 characters), locale, device, logged-in state, model label and date.
- **Cited versus mentioned.** A domain counts as cited when a cited URL's host matches an owned host (lowercased, `www.` removed); the brand is mentioned when the answer text names it. Keep the two counts separate.
- **Who runs it.** The user, or a user-owned collector that follows the collector contract below. This plugin bundles no AI-answer collector and never scrapes search result pages.

## Observation states

| Status | Meaning | Counts in the denominator |
| --- | --- | --- |
| `valid_present` | A usable answer cites an owned URL | Yes |
| `valid_absent` | A usable answer cites no owned URL | Yes |
| `empty` | No usable answer (refusal, no AI answer shown, blank) | No; reported separately |
| `error` | The sample failed (timeout, block, collector error) | No; reported separately |

- A timeout or a block is never a zero citation. A failed observation never triggers a content change.
- Discard a read in which more than half of the samples are `empty` or `error`, and record why (heuristic adopted from eGEOagents' measurement guard).
- When a group has no valid samples, report "no computable result", never 0%.
- Observations are append-only. Corrections are new records that reference the old one.

Metrics, each with raw counts and denominators:

| Metric | Definition |
| --- | --- |
| Citation rate | `valid_present / (valid_present + valid_absent)` per surface and query class |
| Mention rate | Valid answers that name the brand / valid answers |
| AI answer rate | Valid answers / all samples, reported separately because some queries show no AI answer at all |
| Support accuracy | Cited statements that the cited page actually supports / cited statements checked |
| Query stability | Share of repeats of the same query that agree on present or absent |

## Hold-outs and controls

- **Control pages.** Unchanged pages of the same type and topic, read with the same panel at the same times. Report the change on target pages minus the change on control pages ("delta versus control"), never the raw delta.
- **Hold-out queries.** Show whether gains extend beyond the queries the rewrite was tuned for.
- **One attributable change.** Two changes at once cannot be told apart; a labelled batch is evaluated only as a batch.
- **Confounders to record.** Other releases, campaigns, seasonality, engine interface or model changes, and Google updates (`SG updates --since 2026-09`; an overlap with an update is a hypothesis, never proof, [F-T-36](current-facts.md#f-t-36)).

## Read-back windows

Fix the windows before the change ships and do not act on readings inside a window.

| Change type | Read-backs after deployment |
| --- | --- |
| Content refresh or section rewrite on an existing page | 7, 14, 28 and 56 days |
| New page or new asset | 14, 28, 56 and 90 days |
| Technical fix (access, rendering, status codes) | Daily for 7 days, then 28 days |
| AI surfacing panels | Weekly, read against the fixed windows above |

`SG ledger status .seo-geo-god/ledger` lists experiments whose 7, 14, 28 or 56 day read-backs are due. Search Console data lags by a few days; read layer 4 windows after the data has settled.

## Decisions

| Decision | When |
| --- | --- |
| Promote | The pre-registered primary metric beats control by at least the agreed minimum change, guardrails hold, data quality is intact, and the decision owner accepts it |
| Keep testing | Only under a continuation rule written before the test (for example one more read-back) |
| Rollback | A guardrail is breached (traffic, conversions, errors, legal or safety concerns), at any time |
| Unproven | Everything else. No significant difference is not proof of no effect |

Do not promote when the sample is too small, attribution is dirty, exclusions changed after the fact, the window was chosen after seeing results, collection failed mid-window, or only a proxy improved while the declared outcome did not. Record the decision in the experiment record and name who made it.

## Statistics

- **Wilson interval** for a rate of k successes in n valid samples, with z = 1.96 for 95%:
  center = (p + z²/2n) / (1 + z²/n), half-width = z·√(p(1 − p)/n + z²/4n²) / (1 + z²/n), where p = k/n. Example: k = 3, n = 10 gives 0.1078 to 0.6032. `SG ledger summary` reports rates with these intervals.
- **Two-proportion z-test** for target versus control rates: pooled p = (k1 + k2)/(n1 + n2), z = (p1 − p2) / √(p(1 − p)(1/n1 + 1/n2)). Report the effect and its interval, not only a p-value.
- **Dependence.** Repeated samples of one query are not independent users; when in doubt treat the query as the unit and aggregate per query first, then across queries.
- **Small or many comparisons.** Small samples are exploratory. Many surfaces and classes multiply false positives; pre-register the primary comparison.
- **Non-randomized changes.** Use a matched control, a before and after comparison of target against control (difference in differences), or an interrupted time series, and say which.
- Defaults such as 95% intervals are conventions, not truths; declare them before the test.

## Data sources

| Source | What it shows | Limits | Fact |
| --- | --- | --- | --- |
| Search Console Performance | Clicks, impressions, CTR, position; AI Mode is included in "Web" totals | Final data lags a few days; anonymized queries | [F-T-50](current-facts.md#f-t-50) |
| Search Console generative-AI reports | Impressions for AI Overviews and AI Mode by page, country, device and date | No API mentioned; third-party reports say no clicks or queries | [F-AI-13](current-facts.md#f-ai-13) |
| Bing Webmaster Tools AI Performance | Citations, cited pages, sampled grounding queries across Copilot and Bing AI summaries | Public preview; UI or CSV export only, no API method | [F-AI-20](current-facts.md#f-ai-20), [F-T-53](current-facts.md#f-t-53) |
| GA4 default channel "AI Assistant" | Sessions with medium `ai-assistant` or a referrer on Google's AI assistant list | AI Overviews and AI Mode stay in Organic Search; launch date third-party | [F-AI-30](current-facts.md#f-ai-30) |
| `utm_source=chatgpt.com` | ChatGPT referral tagging | Seen only in snippets; needs verification | [F-AI-03](current-facts.md#f-ai-03) |
| Server access logs | Claimed AI bot hits and AI referrers per URL | User agents are claims; verify by IP list or reverse DNS | [ai-crawlers.md](ai-crawlers.md#verification) |
| Prompt panels in the ledger | Citation and mention rates per surface | Manual or user-collected; stochastic | this file |

GA4 custom channel group for AI referrals (our construction, anchored so it works with full or partial matching; place it above "Referral" and apply it to Session source; verify the hosts against your own data):

```text
^(.*\.)?(chatgpt\.com|chat\.openai\.com|openai\.com|perplexity\.ai|gemini\.google\.com|bard\.google\.com|copilot\.microsoft\.com|edgeservices\.bing\.com|claude\.ai|chat\.deepseek\.com|deepseek\.com|meta\.ai|grok\.com|x\.ai|chat\.mistral\.ai|you\.com|phind\.com|kagi\.com)$
```

Do not also require medium = referral, or UTM-tagged ChatGPT visits are missed. `kagi.com`, `you.com` and `phind.com` also run classic search. Many AI-app visits arrive with no referrer and land in Direct, so every AI referral count is a floor. Referral traffic proves an answer linked the site, not that it cited it prominently. Offline counts: `SG referrers ga4.csv` for GA4 exports, `SG referrers access.log --log --bots` for logs (bot counts labelled "claimed (unverified)").

Independent research found that Google users clicked a result in 8% of visits with an AI summary versus 15% without, and a link inside the summary in 1% (March 2025 data) ([F-AI-33](current-facts.md#f-ai-33)). Use it as context for flat or falling clicks, not as a forecast for one site.

## Ledger

The ledger is an append-only local record under `.seo-geo-god/ledger/` in the repository.

```bash
SG ledger init .seo-geo-god/ledger
SG ledger record .seo-geo-god/ledger --json obs.json
SG ledger summary .seo-geo-god/ledger --by surface,query_class --window 2026-11-01:2026-11-30
SG ledger status .seo-geo-god/ledger
```

Observation kinds are `panel` (one AI answer sample), `metric` (a number from Search Console, Bing, GA4, CrUX, logs or a manual read, with its window and segment) and `experiment` (a pre-registered change). Example records (field names must match `schemas/ledger.schema.json`; `SG ledger record` refuses records that do not, and refuses duplicates):

```json
{"kind": "panel", "surface": "perplexity", "query": "how to send a recurring invoice", "query_class": "informational", "holdout": false, "status": "valid_present", "cited_urls": ["https://example.com/guides/recurring-invoices/"], "cited_statement": "Recurring invoices repeat on a schedule you set.", "locale": "en-US", "device": "mobile", "logged_in": false, "model_label": null}
```

```json
{"kind": "experiment", "hypothesis": "Answer-first rewrite of section s03 raises the Perplexity citation rate for q05", "change": "content/guides/recurring-invoices.md section s03", "target_urls": ["https://example.com/guides/recurring-invoices/"], "control_urls": ["https://example.com/guides/payment-reminders/"], "deployed_at": "2026-11-05", "metric": "citation_rate", "baseline_ref": "panel reads 2026-10-20 and 2026-10-27", "readback_days": [7, 14, 28, 56], "decision": null, "note": "plan .seo-geo-god/plans/exp-2026-11-05-recurring.md"}
```

No personal data goes in the ledger. Never record an observation that did not happen; an estimate is not an observation.

## Collector contract

Any script or connector that feeds the ledger, whether the user's own or a documented connector ([connectors.md](connectors.md)), must:

1. Be deterministic and free of model calls: the same input gives the same record.
2. Read configuration from the project file and credentials from environment variables, never printing or logging secret values.
3. Append versioned JSON lines, one per observation, each with a version, a UTC timestamp and a natural key.
4. Never rewrite or delete history; corrections are new records.
5. Be safe to re-run: two runs produce two observations with distinct timestamps.
6. Write data only, never interpretations, plans or content.
7. Fail loudly: exit non-zero on authentication, network, schema or budget failure and write no record for that observation.
8. Support a fixture mode so it can be tested offline.
9. Run only with the user's consent, within the provider's terms, with bounded request counts and any paid usage approved in advance.

Adapted in our own words from the eGEOagents collector contract (MIT).

## Validating a rubric

Any score that claims to predict citation (a citability heuristic, an LLM judgment, a vendor "AI visibility score") needs validation against real citations before anyone relies on it.

1. Pre-register: the rubric version, the query set, the metric (for example mean per-query ROC AUC), the pass threshold, the minimum sample and what happens on pass and on fail.
2. Positives are URLs a surface cited for each query; negatives are other top results for the same query that were not cited.
3. Score every candidate independently under blind IDs derived from the query and text, so the scorer cannot tell which page is "ours".
4. Collect once and evaluate once; no re-runs, prompt edits or threshold changes after seeing numbers.
5. Report the result with a bootstrap interval, including failures.

eGEOagents followed this method for its LLM judge and failed its pre-registered gate in every run (mean AUC between 0.559 and 0.649 against a 0.65 gate; project self-report, https://github.com/mverab/eGEOagents). That is the expected starting point for any unvalidated rubric, including this plugin's citability score.

## Reporting language

- Describe before and after outcomes as observations: "after the change, the Perplexity citation rate for the panel moved from 2 of 15 to 6 of 15 valid samples, while control pages moved from 3 of 15 to 3 of 15", with intervals. Do not write "the rewrite caused".
- Mark every surface that was not sampled as "not measured", and every empty group as "no computable result".
- Keep the states separate: prepared, implemented locally, deployed, submitted, measured.
- Print the facts' as-of date (2026-11-01) and any re-check dates the conclusions depend on.

## Needs verification

- Search Console generative-AI report contents beyond impressions.
- GA4's internal AI assistant list and launch date.
- Referrers sent by each AI app and AI browser.
- Whether a given assistant re-fetches a URL supplied in the prompt or answers from a cached index; confirm per surface in server logs before treating an explicit-URL test as a test of the current page.
