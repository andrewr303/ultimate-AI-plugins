# HypeStake platform map

Read this before moving any part of this plugin into HypeStake. It compares the plugin's provider facts and identity rules with what the HypeStake platform source sends and depends on. The re-integration contract (field mapping, contact-rule conflicts, tool contracts, boundary rules) is in [hypestake-integration-contract.md](hypestake-integration-contract.md).

Checked against HypeStake source `77a68e5c` on 2026-11-10. Read only. No API call was made. Paths below are relative to the HypeStake repository root unless they start with `plugin:` (this plugin) or `star:` (the STAR project, `projects/hypestake-star/` in the environment repository).

## How evidence was weighed

- **Platform code that runs in production and the platform's local spec copy** (`docs/integrations/vendor-docs/research-apis/scrape-creators-openapi.yaml`, checked 2026-09-26, 183 paths) are stronger evidence for request shapes HypeStake already sends: they are exercised by real calls and tests.
- **The plugin's 2026-11-02 check of the live combined spec** (197 paths) is newer. Where the two disagree about something that can change upstream, newer evidence is not automatically stronger, and neither is overwritten. Those rows are listed as unresolved.
- Nothing here was re-checked against the live vendor. A row marked "fixed" changed plugin text; the plugin text now carries "Checked against HypeStake source 77a68e5c".

## Vocabulary

| Plugin text | HypeStake noun (`CONTEXT.md`) | Rule |
|---|---|---|
| creator, influencer | **Creator** | Use Creator for the platform account. "Influencer" stays only in trigger phrases a user might type. |
| brand, advertiser, sponsor | **Brand** | Use Brand for the account that issues deals. |
| creator score (`scripts/creator_score.py`, `src/creator-score.ts`) | none. It is **not** a Match Score | Match Score is pairwise (a Creator Genome against a Brand Profile, from the matching engine or Match Score v2). This score describes one Creator against one research brief from public data, has gates G1 to G5, and is a judgment-default summary. Never display it as a Match Score, a fit score, CERS, PRI, GAV or PRS. In HypeStake it would be advisory evidence for STAR Scout, not a fourth scoring system. |
| shortlist, `qualified` | Creator Finder `qualification`, STAR `Qualification` | Different rules. The plugin's `qualified` is a research status; it never sets a Finder outcome. |
| outreach | Offer, Deal Proposal | Outreach here only finds a contact. Choosing an Offer or a Deal Proposal is a HypeStake product decision outside this plugin. |

## Provider facts: discrepancy table

| # | Plugin claim (before this change) | Platform source | Stronger evidence | Outcome |
|---|---|---|---|---|
| 1 | `cache_max_age` is a number of "days" | `src/shared/social-scrape/client.ts` `CACHE_MAX_AGE_VALUES` = `1d`, `3d`, `7d`, `14d`, `30d`; the local spec declares the same string enum | Platform: production code plus spec enum | **Fixed** in `skills/scrapecreators-api`, `skills/creator-contact-capture`, `references/contact-capture-rules.md` |
| 2 | API key in `SCRAPECREATORS_API_KEY` | `SCRAPE_API` in Trigger and Render code; Scout reads `SCRAPE_API` or `SCRAPECREATORS_API_KEY` (`docs/integrations/vendor-docs/research-apis/scrapecreators HypeStake endpoint map.md`) | Both true for their runtime | **Fixed**: the skill notes that HypeStake runtimes use `SCRAPE_API`. The plugin keeps its own variable name |
| 3 | Auth header `x-api-key` | `client.ts` sends `x-api-key`; spec `securitySchemes` names `x-api-key` | Agree | No change |
| 4 | A cache hit costs 0 credits | `client.ts` reads `credits_charged` (0 on a hit), `cached`, `cached_at`, `credits_remaining` from the body; `normalize.ts` `responseObservedAt` dates a cached response by `cached_at`, and null when it is missing | Platform adds the fields | **Fixed**: the skill now names these fields and says a cache hit's `as_of` is `cached_at`, not the fetch time |
| 5 | "a failed request is retried, not recorded as no email" (`/v1/find-creator-emails`) | Scout: "a failed or timed-out call is never re-sent" in a run (`docs/integrations/api-calls/features/web-research.json`); Genome: an `error` receipt is retried after one day; HypeStake rule: never resend a paid request on an uncertain outcome | Platform: explicit rule | **Fixed**: a failure is recorded as unknown, never as "no email", and is not re-sent in the same run after a timeout or transport error |
| 6 | Search results carry audience counts | Endpoint map section 3: the spec's search examples zero-fill `follower_count`, `aweme_count`, `following_count`, so HypeStake reads a 0 from its three search lanes (Instagram profile search, TikTok user search, TikTok keyword search) as unknown. Whether live responses zero-fill is not established | Platform: derived from the spec examples, not from live responses | **Fixed** in `skills/scrapecreators-api` and `skills/creator-discovery` |
| 7 | Treat Instagram `like_count` 0 as missing | Endpoint map section 5: `like_and_view_counts_disabled: true`, or a like count of 0 on a post with comments, makes likes and views unknown | Agree; platform names the flag | **Fixed**: the flag is named in `skills/scrapecreators-api` |
| 8 | A post with no `age_hours` counts as settled (`creator_score.py`) | Scout: settled posts are at least 72 hours old (336 on YouTube), "unknown age left out" | Platform, and the HypeStake rule that unknown is not zero | **Fixed in code**: unknown age is now excluded and counted as `excluded_unknown_age`; the command line takes `min_age_hours` |
| 9 | Only 36 of 197 spec paths accept `cache_max_age` | `client.ts` `CACHEABLE_PATHS` lists 35 paths "per the OpenAPI spec (2026-09)"; the local spec has 35 `cache_max_age` parameters | Different dates; both may be right | **Unresolved**. Re-count from the live spec before relying on either list |
| 10 | `/v1/find-creator-emails` exists, takes `cache_max_age`, 10 credits with an email, 1 when empty | Not in the local spec (2026-09-26) and not called by the platform | Only the plugin's 2026-11-02 check | **Unresolved**. Treat as Unverified for HypeStake until it is added to `docs/integrations/api-calls/` |
| 11 | `/v1/instagram/search/profiles` takes only `query`, no pagination, enriches the first 10 | Foundry lane sends `query` and `cursor` (up to 2 pages); the endpoint map marks the plugin's claim "Unverified, reported 2026-11-02 by an external research pack" | Undecided | **Unresolved**. The platform already records it as an open question |
| 12 | Spec path count 197 | Local spec copy 183 paths (2026-09-26) | Different dates | Unresolved, not a conflict |
| 13 | LinkedIn company posts: max 7 pages (vendor pack, not re-checked) | `BRAND_GENOME_LINKEDIN_POST_PAGES`, "provider max 7" | Corroborated | **Fixed**: label now says corroborated by HypeStake docs |
| 14 | No SoundCloud or Spotify rows | `src/shared/social-scrape/endpoints.ts`: `/v1/soundcloud/artist` (handle), `/v1/soundcloud/artist/tracks` (handle), `/v1/spotify/artist` (url) | Platform: production code | **Fixed**: two rows added to the Profiles table |
| 15 | `/v1/find-social-profiles`: 10 credits live, 0 cached, confidence-scored | `findSocialProfiles.ts`: source platforms instagram, tiktok, youtube, twitter, facebook; confidence clamped to 0..1; HypeStake writes a URL only at confidence 0.8 or higher; an empty `profiles` list means the handle did not validate | Agree; platform adds rules | **Fixed**: vetting notes the 0.8 write threshold and the empty-list meaning |
| 16 | Errors are not typed | `client.ts` `SCRAPE_ERROR_KINDS`: 404 or an HTTP-200 not-found body is `not_found`, 402 `credits_exhausted`, 401 `provider_auth`, 403 `source_blocked`; 401 and 402 stop the whole run | Platform | **Fixed**: one line in the skill |
| 17 | Platform paths `/v3/tiktok/profile/videos`, `/v2/instagram/user/posts`, `/v1/youtube/channel-videos`, `/v1/twitter/user-tweets`, `/v1/threads/user/posts`, `/v1/bluesky/user/posts`, `/v1/facebook/profile/posts` | Same paths in `endpoints.ts` `PLATFORM_ENDPOINTS` | Agree | No change |
| 18 | `/v1/tiktok/user/audience` costs 26 credits | Endpoint map section 6: 26 credits, kept behind `SCRAPE_ENABLE_AUDIENCE=false` | Agree | No change |
| 19 | Bio text may hold a business email | `normalize.ts` `sanitizeText` replaces every email and phone number in bios and captions with `[redacted-email]` and `[redacted-phone]` before storage | Platform policy | Not a provider fact. See the integration contract: contact capture must not read addresses out of stored snapshots |

## Handle and identity rules

| # | Plugin rule | Platform source | Assessment |
|---|---|---|---|
| H1 | Entity key `(entity, platform)`; entity is the lowercase handle without `@` | `handles.ts` `stripAt` removes leading `@` and keeps case for the request; `social_account_follower_history.handle_series_key` is the lowercase handle; STAR `normHandle` (`star:src/finder/domains.ts`) lowercases and also drops `.`, `_` and `-` | Compatible with the platform's series key. STAR's `normHandle` is a blocking and comparison key, not a storage key: do not store it as the plugin's entity |
| H2 | Never parse URLs to decide identity | `handles.ts` `targetFromUrl` derives a request handle from a validated URL path; `identity.ts` refuses handle and name similarity as identity evidence; STAR `identity.ts` gives a URL-structure handle no weight | Compatible: URL parsing is used for request targets, never identity |
| H3 | One person on two platforms is two records, never merged by address, domain or display name | STAR `resolveIdentity`: only `link` and `same_account` merge in storage; `probable` is never merged | Compatible. A plugin `business_inbox` must never be used as identity evidence, which STAR also never does |
| H4 | Mastodon entity `username@instance.domain` | Mastodon is not a HypeStake `SocialPlatform` (`types.ts` `SOCIAL_PLATFORMS`) | The record has no platform column to land in. Keep it as a web candidate |
| H5 | YouTube handle without `@`, or a channelId, or a URL | `handles.ts` and `findSocialProfiles.ts`: channel endpoint takes the URL; channel-videos takes `handle` or `channelId`; `/c/` and `/user/` URLs get no videos call; find-social-profiles accepts `@handle` or a 24-character `UC...` id only | Platform is stricter. The skill now says find-social-profiles refuses `/c/` and `/user/` names |
| H6 | X handle passed as `twitter` | `findSocialProfiles.ts`: `x` is an alias, but HypeStake always sends `twitter` | Agree |

## What was not checked

- The live ScrapeCreators spec, docs and prices. Every "Last verified 2026-11-02" in the plugin is still the plugin's own check.
- Whether HypeStake's Scout Python client (`services/scout_agent/`) matches this table beyond what its API docs state.
- `config/scrapecreators-pricing.json` in HypeStake was not compared.
