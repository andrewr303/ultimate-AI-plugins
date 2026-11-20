# Creator discovery data sources

Data-layer reference for finding creators and judging what each source can return. Written 2026-11-02.

**Evidence labels.**
- **Verified**: checked on 2026-11-02 against a primary page, the OpenAPI spec or a live call. Items carry "Last verified 2026-11-02" where a price, quota, path or figure appears.
- **Summariser-read**: a primary page read through a text summariser, with figures not re-checked against the raw page.
- **Reported**: taken from a secondary source or a vendor's own text and not re-checked.
- **Reported by a third-party pack (unlicensed), not re-measured**: a claim that only the unlicensed discovery pack makes. Use it as a lead, and test before a decision depends on it.
- **Unverified**: nobody has checked it, so test before relying on it.

## 1. Provenance and corrections

The findings here were taken from two uploaded packs: the ScrapeCreators skill pack (MIT, vendor-written) and a public discovery pack that has no license. Where a finding came from the unlicensed pack, it was independently re-sourced from primary pages, the OpenAPI spec or live tests wherever that was possible, and the rest carry the label above.

Verification changed these claims that circulate in vendor text and in the packs (Last verified 2026-11-02):

- **Endpoint count.** The ScrapeCreators combined spec lists 197 paths and 200 operations, plus 4 documented paths that are missing from it. The docs still say "110+", which is stale. A figure of 175 also circulates. Its origin is unverified and it matches no primary page, so it is probably an earlier snapshot.
- **"Only one vendor sells TikTok audience data."** Refuted. ScrapeCreators sells the same 26-credit country list, CreatorDB returns gender and age bands, and SocialCrawl sells a country list at 5 credits.
- **Instagram `/v1/instagram/search/profiles`.** The spec says it returns Instagram's native ranked results, enriches only the first 10, has no pagination, does not search bios or captions and states no cost. Per-call yield figures for it come only from the unlicensed pack (Reported by a third-party pack (unlicensed), not re-measured).
- **Threads official keyword search quota.** A 7-day figure circulates. Meta documents 2,200 queries per rolling 24 hours per user across apps.
- **Instagram `business_email`.** The spec says Instagram profile responses carry it when Instagram supplies it, and `trim=true` drops it. The unlicensed pack reports it null in its own samples, not re-measured. Treat it as unsettled and test a small sample before promising emails.
- **TikTok `search/users` bio.** The spec lists a bio in `user_info`. The unlicensed pack reports it empty in practice, not re-measured. Budget one profile call per person until a sample shows otherwise.
- **LamaTok price.** A figure of $0.001 per request circulates. The pricing page says $0.60 per 1,000 requests at volume and $1 per 1,000 on the popular plan (summariser-read, Last verified 2026-11-02).
- **Vendor choice.** One pack excludes any vendor with a monthly fee. That is a policy choice, not a fact, so this file lists such vendors and marks their billing model.

## 2. Per platform

Each entry covers: no credentials, ScrapeCreators (SC), official API, contact boundary.

### Instagram
- **No credentials.** Reported by a third-party pack (unlicensed), not re-measured: the public web page carries no email and most of it sits behind a login.
- **SC (Verified, Last verified 2026-11-02).** `/v1/instagram/search/profiles` (`query` only, first 10 results enriched). `/v1/instagram/search` returns users, hashtags, places and suggestions. `/v1/instagram/profile` returns bio, links and counts and accepts `cache_max_age`. An age-gated 403 and a "restricted/unavailable" 404 cost 0, and legacy 200 placeholders cost 1. Branch on `errorStatus`, not `success`.
- **Official (Last verified 2026-11-02).** Creator Marketplace API, GA 2025-10-01. It uses Facebook Login and the permissions `instagram_creator_marketplace_discovery`, `instagram_basic`, `pages_manage_metadata`, `pages_show_list` and `business_management`. New apps get standard access, which returns test data only, so production needs advanced access through app review. The brand must pass Meta's eligibility check and accept the Creator Marketplace terms, or calls return error code 10. It needs a Page access token for a Page linked to the brand's Instagram business account (or a BISU token). Endpoint: `GET https://graph.facebook.com/v25.0/<IG_USER_ID>/creator_marketplace_creators`. Rate limit: 5,000 requests per user per hour. Business Discovery looks up a known username for a Business or Creator account and has no search.
- **Definition drift (Last verified 2026-11-02).** For hidden likes, an indirect query returns 0 (2021 changelog) or omits `like_count` (current reference), so treat both as "hidden", never as zero engagement. Business Discovery `view_count` has combined Instagram and Facebook views for crossposted video since April 2026. The "Paid partnership" label can be written through the Content Publishing API, and no read field is documented.
- **Contact.** `business_email` and `business_phone_number`: see section 1, unsettled. For emails use section 3.

### TikTok
- **No credentials.** Unverified: whether anything useful can be read from the public page.
- **SC (Last verified 2026-11-02).** `/v1/tiktok/search/users` (`query`, `cursor`, `trim`), `/v1/tiktok/search/keyword`, `/v1/tiktok/search/hashtag`, `/v1/tiktok/profile` (1 credit assumed, cost not stated in the spec), `/v1/tiktok/user/audience` (26 credits, `handle` only, country list only, no `cache_max_age`). `/v1/tiktok/creators/popular` has marketplace-style filters in the spec: follower count, creator country, audience country and sort order.
- **Other vendors.**
  - SociaVault: `GET https://api.sociavault.com/v1/scrape/tiktok/demographics`, 26 credits, country only (Verified from its docs, Last verified 2026-11-02).
  - CreatorDB: `POST https://apiv3.creatordb.app/tiktok/audience` returns country shares, gender ratio, average age and age bands. Summariser-read, not re-checked, Last verified 2026-11-02. The default request shows `creditsUsed` 1, but pay-as-you-go pricing is not confirmed and its method is not stated.
  - SocialCrawl: `GET https://www.socialcrawl.dev/v1/tiktok/user/audience` costs 5 credits uncached, 0 if cached, with a 30-minute cache. It returns countries, and age, gender and state only when the creator has a public Shop marketplace card. Summariser-read, not re-checked, Last verified 2026-11-02. The vendor's own page contradicts itself on whether age and gender are returned, so treat the Shop-card condition as unconfirmed.
  - TikHub: no profile-level audience route, only a per-video one that needs the creator's own cookie (Verified from its OpenAPI paths, Last verified 2026-11-02).
- **Official.** The Research API is for academic, non-commercial use (Verified from TikTok's page, Last verified 2026-11-02). TikTok One creator marketplace access is company-only (Reported, Unverified).
- **Contact.** No structured contact field. Leads are the bio text and the bio link.

### YouTube
- **No credentials.** Reported by a third-party pack (unlicensed), not re-measured: the channel About page HTML holds the description and links, the "view email" button sits behind login and a CAPTCHA, and the Data API has no field for it.
- **SC.** `/v1/youtube/search`, `/v1/youtube/channel`, `/v1/youtube/channel-videos` (hyphen), `/v1/youtube/video/transcript` (1 credit, no AI, any length when public captions exist). Last verified 2026-11-02.
- **Official (Last verified 2026-11-02).** YouTube Data API v3: `search.list` has its own bucket of 100 calls per day at 1 quota each (pagination counts), all other endpoints share 10,000 units per day, and quotas reset at midnight Pacific. The quota page was updated 2026-10-15. `videos.list` accepts `part=paidProductPlacementDetails` (`hasPaidProductPlacement`). Whether an API key alone can read it is Unverified, so test with one live call. From 2026-08-24 `viewCount` counts autoplay and hover starts, so view baselines spanning that date are not like-for-like.
- **Contact.** Reported by a third-party pack (unlicensed), not re-measured: addresses typed into the links section can appear as redirect URLs with the real address in a query parameter.

### X (Twitter)
- **No credentials.** Reported by a third-party pack (unlicensed), not re-measured: anonymous pages give display name and bio only.
- **SC.** `/v1/twitter/profile`, `/v1/twitter/user-tweets` (about 100 most popular, not chronological), `/v1/twitter/search/posts`. There is no user search. Last verified 2026-11-02.
- **Official (summariser-read, Last verified 2026-11-02).** Pay per use: post reads $0.005 per resource, user reads $0.010, follower or following reads $0.010, likes reads $0.001, post create $0.015 ($0.200 with a URL), counts $0.005 recent and $0.010 all. The cap is 3 million post reads per billing cycle. The page says prices can change, so check the Developer Console.
- **Not adopted.** The unlicensed pack drives a logged-in browser session through a third-party library. That risks the person's account and sits in the legal area covered by `outreach-compliance`, so this plugin does not use it.
- **Contact.** None in profiles. `/v1/find-creator-emails` accepts X handles.

### Threads
- **No credentials.** Reported by a third-party pack (unlicensed), not re-measured: the profile page's Open Graph tags give name, follower count and bio, with no external links and no discovery.
- **SC (Last verified 2026-11-02).** `/v1/threads/search` searches posts, and the spec says it returns only 10 results per request. `/v1/threads/search/users` takes a query, and the spec states no result cap for it. `/v1/threads/profile` returns the profile. The spec describes search results as post data with user info. Whether that user info carries follower counts or bio is Unverified (the unlicensed pack reports identity fields only, not re-measured), so budget one profile call per person until a sample shows otherwise.
- **Official (Last verified 2026-11-02).** `threads_keyword_search` plus `threads_basic`. Until the app is approved, search covers only the signed-in user's own posts. The limit is 2,200 queries per rolling 24 hours per user across all apps. Repeat queries count and zero-result queries do not. No account search is documented.

### Bluesky
- **No credentials.** Unauthenticated test on 2026-11-02: `public.api.bsky.app` `app.bsky.actor.searchActors` returned 200. `searchPosts` returned 403 on `public.api.bsky.app`, 200 on `api.bsky.app` and 401 on `bsky.social`, so plan post search around an app password.
- **SC.** Profile, user posts and single post only. No search.

### Mastodon
- **No credentials (Last verified 2026-11-02).** `GET /api/v2/search` is public for `type=accounts` and hashtags without `resolve` or `offset`. Full-text status search needs a token, and unauthenticated `type=statuses` returned empty arrays on mastodon.social. `resolve=true` returned 401. `GET /api/v1/directory` returned 200. Results and limits are per instance, so dedupe on `username@domain`.
- **Contact.** The account object has no email field. `fields[].verified_at` is the instance's own proof that the person controls a linked site (Reported from Mastodon's API docs, not re-checked).

### Reddit
- **Official.** Primary pages were blocked during research, so everything here is Reported: a free tier for non-commercial use, and a separate agreement for commercial use. Whether self-serve approval exists is Unverified. The unlicensed pack reports the anonymous `.json` route retired on 2026-05-28 (Reported by a third-party pack (unlicensed), not re-measured), so do not plan around it.
- **SC.** `/v1/reddit/search`, `/v1/reddit/subreddit`, `/v1/reddit/subreddit/search`, `/v1/reddit/post/comments`. Subreddit names are case-sensitive.
- **Contact.** Reported by a third-party pack (unlicensed), not re-measured: the user object exposes only a verified-email boolean, and its follower field reads 0 for everyone, so do not treat it as data.

### LinkedIn and Facebook
- **LinkedIn.** SC has `/v1/linkedin/profile`, `/v1/linkedin/company`, `/v1/linkedin/company/posts` and `/v1/linkedin/ads/search`. Reported by a third-party pack (unlicensed), not re-measured: there is no public people search, the official API is partner-gated, and contact details show only to first-degree connections.
- **Facebook.** SC has profile, posts, reels, groups and the ad library. The Facebook Creator Discovery API reached GA on 2025-10-06 (Last verified 2026-11-02). Its access terms are Unverified, so assume they mirror the Instagram review process.

### Newsletters, blogs, podcasts, code hosts
- **Substack and Patreon.** SC has no endpoint for either (Verified absent, Last verified 2026-11-02).
- **Other key-free surfaces.** Reported by a third-party pack (unlicensed), not re-measured: podcast directories, code hosts, avatar services and some blogging platforms expose author emails in places, and some hosts block honest crawlers. None of these sources is in the `outreach-compliance` policy table, so skills do not fetch them.

## 3. Contact-info boundary

| Source | Owner | What you can get | Cost (Last verified 2026-11-02) |
|---|---|---|---|
| `GET /v1/find-creator-emails` (`platform`, `handle`, `cache_max_age`) | `creator-contact-capture` | Looks at the bio, contact links, link-in-bio pages and a bounded scan of the creator's site. Platforms: Instagram, TikTok, YouTube, X, Facebook. Returns deduplicated addresses with a public source URL and source type for each, and the sources array is empty only when the source is internal. No guessing and no deliverability check. An address may belong to the creator, their management or a booking contact. An empty partial result is not proof that no address exists, and a failed request is retried, not read as "no email". | 1 credit if empty, 10 if any email is returned, 0 on a cache hit, bad input, a missing source profile or a failed lookup |
| `GET /v1/find-social-profiles` (`platform`, `handle`, `cache_max_age`) | `creator-vetting` | Expands link-in-bio pages and links same-handle accounts on other platforms with a confidence score, for identity matching | 10 credits per successful live lookup, 0 on a cache hit. An uncharged 503 is returned if every declared link page fails and nothing else yields a profile |
| Linktree and similar (`/v1/linktree`, `/v1/komi`, `/v1/pillar`, `/v1/linkbio`, `/v1/linkme`) | `creator-contact-capture` | Links and social accounts. Linktree can include `email_address` | 1 credit assumed (cost not stated in the spec) |
| Instagram `business_email` | n/a | See section 1, unsettled | n/a |
| Creator Marketplace API | `creator-discovery` | An email field and a `has_public_contact_email` filter (Reported from the docs summary, not re-checked) | Free call, review and eligibility required |

Everything else in section 2 returns no personal email. Use contact data only within the `outreach-compliance` skill.

## 4. Credentials (variable names only)

Never paste values into chat, logs or committed files. Every name except the ScrapeCreators one is this plugin's own proposal, Unverified as a convention.

| Variable | Used for | Origin |
|---|---|---|
| `SCRAPECREATORS_API_KEY` | ScrapeCreators, header `x-api-key` | ScrapeCreators skill pack |
| `SOCIAVAULT_API_KEY` | SociaVault, header `X-API-Key` | Proposed name |
| `YOUTUBE_API_KEY` | YouTube Data API | Proposed name |
| `X_BEARER_TOKEN` | X API pay-per-use | Proposed name |
| `META_ACCESS_TOKEN`, `IG_USER_ID` | Instagram Creator Marketplace, Business Discovery | Proposed names |
| `THREADS_ACCESS_TOKEN` | Threads API | Proposed name |
| `BSKY_HANDLE`, `BSKY_APP_PASSWORD` | Bluesky authenticated search | Proposed names |

## 5. Pay-as-you-go pricing

All entries Last verified 2026-11-02.

- **ScrapeCreators** (https://scrapecreators.com). Free: $0 with 100 credits, plus up to 7,000 bonus credits claimable. Freelance: $47 for 25,000 credits ($1.88 per 1k). Business: $497 for 500,000 ($0.99 per 1k). Enterprise: custom, 1M+. Credits never expire and every tier includes every API. One credit per request for most endpoints, and the spec states few costs. Cache hits cost 0, but only 36 of 197 paths accept `cache_max_age`. A 26-credit audience lookup is about $0.049 at the Freelance rate and $0.026 at the Business rate (derived).
- **SociaVault** (summariser-read). One-time packs, credits never expire: Free Trial 50 credits; Starter $29 for 6,000; Growth $79 for 20,000; Pro $199 for 75,000; Enterprise $399 for 200,000.
- **X API**: see the X entry above.
- **YouTube Data API**: no charge, quota-limited as above.
- **TikHub** (summariser-read). $0.001 to $0.01 per request depending on endpoint, $5 minimum top-up, and 10 requests per second per account at the start.
- **LamaTok** (summariser-read). $0.60 per 1,000 requests at volume, $1 per 1,000 on the popular plan, 100 free requests.
- **Bright Data Web Scraper** (summariser-read). $1.5 per 1,000 records pay as you go, with 5,000 free records per month.
- **Apify actors** (summariser-read, actor pages). Pay per event, from $1.50 to $2.40 per 1,000 results at the cheapest plan, depending on actor, and higher on the Free plan (for example $2.70 for Instagram search). One TikTok profile actor lists "from $1.00" but its own FAQ says "$5 to scrape 1,000 results", so that page contradicts itself and its figure is excluded here.

## 6. Cost-ordering rule of thumb

This is a derived rule for this plugin, with example numbers of its own.

1. **Compare routes by credits per passing creator.** Divide credits per call, times calls per creator, by the share of creators who pass the filter. A route at 1 credit per call, 2 calls per creator and a 25% pass share costs 8 credits per passing creator. A route at 3 credits per call, 1 call and a 50% pass share costs 6, so the dearer call wins. Measure the three terms on a pilot of about 20 creators per route, because this file carries no measured yield.
2. **Spend nothing before spending the free routes.** Key-free pages, Mastodon, Bluesky actor search and the free official APIs cost no credits. YouTube search is the exception, because its 100 daily `search.list` calls run out fast. Use them for discovery and use `channels.list` and `videos.list` (1 unit each) for enrichment.
3. **Put expensive calls behind cheap filters.** Run `/v1/tiktok/user/audience` (26 credits) and `/v1/find-creator-emails` (10 on a hit) only on a shortlist. With a hit rate h, the expected email cost per creator is 1 + 9h credits, derived from the 1 and 10 credit costs above, so a 30% hit rate costs 3.7 credits per creator.
4. **Reuse the cache.** Pass `cache_max_age` on the 36 paths that accept it before re-pulling the same profiles.
5. **Capability beats price.** If the target population exists on only one platform, or the brief needs audience age and gender (CreatorDB, summariser-read), use the one source that offers it.

## 7. Sources and gaps

- Verified claims from the 2026-11-02 verification pass (`../research/verification-2026-11-02.md`), the vendor research notes in `../research/01-api-vendors.md`, and the ScrapeCreators skill pack (MIT). Findings taken from the unlicensed discovery pack were independently re-sourced where possible and are labelled where not.
- Open items carry an Unverified label in the section where they appear.
