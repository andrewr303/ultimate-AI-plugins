---
name: scrapecreators-api
description: >-
  Use when the user names ScrapeCreators, asks which ScrapeCreators endpoint,
  parameters, response fields or credit cost apply, wants raw data for one
  named account or post (TikTok, Instagram, YouTube, LinkedIn, Facebook,
  Twitter/X, Reddit, Threads, Bluesky, Pinterest, Snapchat, Twitch, Kick,
  Truth Social, TikTok Shop, Google, link-in-bio services), or checks remaining
  credits. For analysis workflows (ad teardown, comment mining, transcript
  analysis, trends, creator discovery, contact capture, vetting) load the
  matching skill, which calls this one for endpoints.
allowed-tools: Bash, Read, Write, WebFetch
license: MIT
homepage: https://scrapecreators.com
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      env:
        - SCRAPECREATORS_API_KEY
    primaryEnv: SCRAPECREATORS_API_KEY
    homepage: https://scrapecreators.com
    tags:
      - scraping
      - social-media
      - tiktok
      - instagram
      - youtube
      - linkedin
      - facebook
      - twitter
      - reddit
      - threads
      - bluesky
      - pinterest
      - snapchat
      - twitch
      - truth-social
      - tiktok-shop
      - google
      - ad-library
      - creator-data
      - transcripts
      - trending
---

# ScrapeCreators API

## Overview

Scrape and extract public data from the platforms below. The combined OpenAPI spec lists 197 paths (200 operations) in about 33 top-level groups (Last verified 2026-11-02, counted from https://docs.scrapecreators.com/openapi.json). Vendor pages say "27+" and "38+" platforms, which are vendor claims. Four more paths are documented per endpoint but missing from that combined spec (marked "not in combined spec" in the tables below). The docs pages still say "110+ endpoints", which is stale. Re-count from the spec before quoting a number.

**Base URL:** `https://api.scrapecreators.com`

Get your API key at https://scrapecreators.com and export it as `SCRAPECREATORS_API_KEY`. HypeStake runtimes read the same key from `SCRAPE_API` (Scout also accepts `SCRAPECREATORS_API_KEY`) and never send it to the browser (checked against HypeStake source 77a68e5c, 2026-11-10). Pay-as-you-go pricing: Free tier 100 credits, Freelance $47 for 25,000 credits, Business $497 for 500,000 credits, credits never expire (Last verified 2026-11-02, https://scrapecreators.com).

## When to Use

- The user wants public profile, post, comment, transcript, follower, ad-library, trend or search data from a social platform.
- The user names ScrapeCreators, asks which endpoint returns a field, or asks about credit cost or balance.
- The user asks what `/v1/find-creator-emails` or `/v1/find-social-profiles` takes and costs. `creator-contact-capture` owns the first and `creator-vetting` owns the second, so those skills decide when to call them. Here you only read the params and cost.

Skip it when an official free API already answers the question (see `../../references/data-sources.md`) or when the data sits behind a login.

## Workflow

1. Pick the endpoint from the Intent Routing tables below.
2. Fetch its per-endpoint OpenAPI spec for exact params and the example response.
3. Check the Credit Costs table. Warn the user before any call that costs more than 1 credit, and pass `cache_max_age` where the endpoint accepts it, because a cache hit costs 0 credits. The value is a string, one of `1d`, `3d`, `7d`, `14d`, `30d`, not a bare number (checked against HypeStake source 77a68e5c, 2026-11-10).
4. Call the endpoint with `x-api-key`, then paginate with the cursor named in the Pagination table.
5. Report the numbers returned, the credits spent and any field that came back empty. Read the charge from the body: `credits_charged` (0 on a cache hit), `credits_remaining`, `cached` and `cached_at`. Date a cached response by `cached_at`, and record its `as_of` as unknown when `cached_at` is missing, never as the fetch time (checked against HypeStake source 77a68e5c, 2026-11-10).
6. Treat failures by type: HTTP 404 or an HTTP-200 body with `error: "not_found"` or `errorStatus: 404` is not found; 402 means credits are exhausted and 401 an invalid key, and both stop the run; 403 means the source blocks that one resource. A timeout or network error is an unknown outcome: record it as unknown and do not re-send a paid call in the same run (checked against HypeStake source 77a68e5c, 2026-11-10).

## Output Format

Return the answer first, then a short evidence block: endpoint path, key params, credits used, and caveats such as empty fields or partial pages. Put raw JSON in a file when it exceeds a screen.

## How to Call

Nearly all endpoints use GET requests. Three paths also accept POST with a JSON body: `/v1/facebook/adLibrary/search/ads`, `/v1/facebook/adLibrary/company/ads`, `/v1/reddit/post/comments` (Last verified 2026-11-02). Pass query params in the URL and authenticate with the `x-api-key` header. Responses are JSON.

```bash
curl -s "https://api.scrapecreators.com/v1/tiktok/profile?handle=charlidamelio" \
  -H "x-api-key: $SCRAPECREATORS_API_KEY"
```

Or with `fetch`:

```javascript
const res = await fetch(
  "https://api.scrapecreators.com/v1/tiktok/profile?handle=charlidamelio",
  { headers: { "x-api-key": process.env.SCRAPECREATORS_API_KEY } }
);
const data = await res.json();
```

Endpoint paths mostly follow `/v1/platform/action`, but some use a hyphen (`/v1/youtube/channel-videos`, `/v1/twitter/user-tweets`, `/v1/instagram/basic-profile`, `/v1/detect-age-gender`), so copy paths from the tables below. The tables list each endpoint path and its required params.

### API Spec

Each endpoint has its own OpenAPI spec at `https://docs.scrapecreators.com/{path}/openapi.json`.

For example: https://docs.scrapecreators.com/v1/tiktok/profile/openapi.json

**Important:** Once you've determined which endpoint(s) to call from the routing tables below, fetch the single-endpoint OpenAPI spec first to get the full parameter details, types, and example response before making the actual API call.

The combined spec is at https://docs.scrapecreators.com/openapi.json (large file, so prefer the per-endpoint specs above). It is not the full documented surface: `/v1/reddit/ads/search`, `/v1/reddit/ad`, `/v1/tiktok/videos/popular` and `/v1/tiktok/songs/popular` appear in https://docs.scrapecreators.com/llms.txt and have per-endpoint specs but are absent from it (Last verified 2026-11-02; a 401 without a key shows the route exists, but returning data is Unverified).

## Intent Routing

Map user intent to the right endpoint. After selecting an endpoint, fetch its OpenAPI spec at `https://docs.scrapecreators.com/{path}/openapi.json` for full param details before calling.

### Profiles / User Info
| Platform | Endpoint | Primary Param | Example |
|----------|----------|---------------|---------|
| TikTok | `/v1/tiktok/profile` | handle | `stoolpresidente` |
| Instagram | `/v1/instagram/profile` | handle | `jane` |
| YouTube | `/v1/youtube/channel` | handle, channelId, or url | `ThePatMcAfeeShow` |
| LinkedIn (person) | `/v1/linkedin/profile` | url | `https://www.linkedin.com/in/parrsam/` |
| LinkedIn (company) | `/v1/linkedin/company` | url | `https://linkedin.com/company/shopify` |
| Facebook | `/v1/facebook/profile` | url | `https://www.facebook.com/mantraindianfolsom` |
| Twitter/X | `/v1/twitter/profile` | handle | `elonmusk` |
| Reddit | `/v1/reddit/subreddit/details` | subreddit or url | `AskReddit` |
| Threads | `/v1/threads/profile` | handle | `zuck` |
| Bluesky | `/v1/bluesky/profile` | handle | `jay.bsky.team` |
| Pinterest | `/v1/pinterest/user/boards` | handle | `pinterest` |
| Truth Social | `/v1/truthsocial/profile` | handle | `realDonaldTrump` |
| Twitch | `/v1/twitch/profile` | handle | `ninja` |
| Snapchat | `/v1/snapchat/profile` | handle | `djkhaled` |
| SoundCloud | `/v1/soundcloud/artist` (tracks: `/v1/soundcloud/artist/tracks`) | handle | (used by HypeStake, checked against HypeStake source 77a68e5c, 2026-11-10) |
| Spotify | `/v1/spotify/artist` | url (artist URL only) | (used by HypeStake, checked against HypeStake source 77a68e5c, 2026-11-10) |

### Posts / Content Feeds
| Platform | Endpoint | Primary Param | Example |
|----------|----------|---------------|---------|
| TikTok videos | `/v3/tiktok/profile/videos` | handle | `stoolpresidente` |
| Instagram posts | `/v2/instagram/user/posts` | handle | `jane` |
| Instagram reels | `/v1/instagram/user/reels` | handle or user_id | `jane` or `2700692569` |
| Instagram highlights | `/v1/instagram/user/highlights` | handle or user_id | `jane` or `2700692569` |
| YouTube videos | `/v1/youtube/channel-videos` | handle or channelId | `ThePatMcAfeeShow` |
| YouTube shorts | `/v1/youtube/channel/shorts` | handle or channelId | `starterstory` |
| YouTube playlist | `/v1/youtube/playlist` | playlist_id | `PLP32wGpgzmIlInfgKVFfCwVsxgGqZNIiS` |
| LinkedIn posts | `/v1/linkedin/company/posts` | url | `https://linkedin.com/company/shopify` |
| Facebook posts | `/v1/facebook/profile/posts` | url or pageId | `https://www.facebook.com/pacemorby` |
| Facebook reels | `/v1/facebook/profile/reels` | url | `https://www.facebook.com/Spurs` |
| Facebook photos | `/v1/facebook/profile/photos` | url | `https://www.facebook.com/Spurs` |
| Facebook group posts | `/v1/facebook/group/posts` | url or group_id | `742354120555345` |
| Twitter tweets | `/v1/twitter/user-tweets` | handle | `elonmusk` |
| Reddit posts | `/v1/reddit/subreddit` | subreddit | `AskReddit` |
| Threads posts | `/v1/threads/user/posts` | handle | `zuck` |
| Bluesky posts | `/v1/bluesky/user/posts` | handle or user_id | `jay.bsky.team` |
| Truth Social posts | `/v1/truthsocial/user/posts` | handle or user_id | `realDonaldTrump` |
| Pinterest board | `/v1/pinterest/board` | url | `https://www.pinterest.com/...` |

### Single Post / Video Details
| Platform | Endpoint | Primary Param | Example |
|----------|----------|---------------|---------|
| TikTok | `/v2/tiktok/video` | url | `https://www.tiktok.com/@randomspamvideos25/video/7251387037834595630` |
| Instagram | `/v1/instagram/post` | url | `https://www.instagram.com/reel/DOq6eV6iIgD` |
| Instagram highlight | `/v1/instagram/user/highlight/detail` | id | `18067016518767507` |
| YouTube | `/v1/youtube/video` | url | `https://www.youtube.com/watch?v=Y2Ah_DFr8cw` |
| YouTube community post | `/v1/youtube/community-post` | url | `https://www.youtube.com/post/Ugkxvj2KoApYAXoqLWnKVr6zZe5JjeHrQeP8` |
| LinkedIn | `/v1/linkedin/post` | url | `https://www.linkedin.com/pulse/being-father-has-made-me-better-leader...` |
| Facebook | `/v1/facebook/post` | url | `https://www.facebook.com/reel/1535656380759655` |
| Twitter/X | `/v1/twitter/tweet` | url | `https://twitter.com/elonmusk/status/...` |
| Twitter/X community | `/v1/twitter/community` | url | `https://twitter.com/i/communities/...` |
| Twitter/X community tweets | `/v1/twitter/community/tweets` | url | `https://twitter.com/i/communities/...` |
| Reddit | `/v1/reddit/post/comments` | url | `https://www.reddit.com/r/AskReddit/comments/...` |
| Threads | `/v1/threads/post` | url | `https://www.threads.net/@zuck/post/...` |
| Bluesky | `/v1/bluesky/post` | url | `https://bsky.app/profile/.../post/...` |
| Truth Social | `/v1/truthsocial/post` | url | `https://truthsocial.com/@realDonaldTrump/posts/...` |
| Pinterest | `/v1/pinterest/pin` | url | `https://www.pinterest.com/pin/...` |
| Twitch clip | `/v1/twitch/clip` | url | `https://clips.twitch.tv/...` |
| Kick clip | `/v1/kick/clip` | url | `https://kick.com/...` |

### Comments
| Platform | Endpoint | Primary Param | Example |
|----------|----------|---------------|---------|
| TikTok | `/v1/tiktok/video/comments` | url | `https://www.tiktok.com/@stoolpresidente/video/7499229683859426602` |
| Instagram | `/v2/instagram/post/comments` | url | `https://www.instagram.com/reel/DOq6eV6iIgD` |
| YouTube | `/v1/youtube/video/comments` | url | `https://www.youtube.com/watch?v=dQw4w9WgXcQ` |
| Facebook | `/v1/facebook/post/comments` | url or feedback_id | `https://www.facebook.com/reel/753347914167361` |
| Reddit | `/v1/reddit/post/comments` | url | `https://www.reddit.com/r/AskReddit/comments/...` |

### Transcripts
| Platform | Endpoint | Example | Note |
|----------|----------|---------|------|
| TikTok | `/v1/tiktok/video/transcript` | `url=https://www.tiktok.com/...&lang=en` | also via `/v2/tiktok/video` with get_transcript=true (detail-route pricing in Credit Costs) |
| Instagram | `/v2/instagram/media/transcript` | `url=https://www.instagram.com/reel/...` | AI-powered, latency 10 to 30 s (vendor pack, not re-checked), AI cap 120 s (see Credit Costs) |
| YouTube | `/v1/youtube/video/transcript` | `url=https://www.youtube.com/watch?v=bjVIDXPP7Uk` | also included in `/v1/youtube/video` response |
| Facebook | `/v1/facebook/post/transcript` | `url=https://www.facebook.com/reel/...` | AI cap 120s (see Credit Costs) |
| Facebook ads | `/v1/facebook/adLibrary/ad/transcript` | parameters: see the spec | AI cap 120s (see Credit Costs) |
| Twitter/X | `/v1/twitter/tweet/transcript` | `url=https://twitter.com/...` | AI-powered, latency not measured (see Credit Costs) |

### Search
| Platform | Endpoint | Primary Param | Example |
|----------|----------|---------------|---------|
| TikTok users | `/v1/tiktok/search/users` | query | `funny` |
| TikTok videos (keyword) | `/v1/tiktok/search/keyword` | query | `funny` |
| TikTok videos (hashtag) | `/v1/tiktok/search/hashtag` | hashtag | `fyp` |
| TikTok top (photos+videos) | `/v1/tiktok/search/top` | query | `funny` |
| Instagram profiles | `/v1/instagram/search/profiles` | query | `yoga teacher` |
| Instagram users, hashtags, places | `/v1/instagram/search` | query | `yoga` |
| Instagram reels | `/v2/instagram/reels/search` | query | `dogs` |
| YouTube | `/v1/youtube/search` | query | `funny` |
| YouTube hashtag | `/v1/youtube/search/hashtag` | hashtag | `funny` |
| Reddit (all) | `/v1/reddit/search` | query | `best programming languages` |
| Reddit (in subreddit) | `/v1/reddit/subreddit/search` | subreddit + query | `AskReddit` + `funny` |
| Threads posts | `/v1/threads/search` | query | `AI` |
| Threads users | `/v1/threads/search/users` | query | `zuck` |
| Pinterest | `/v1/pinterest/search` | query | `home decor` |
| Google | `/v1/google/search` | query | `best restaurants in NYC` |

### Ad Libraries
| Platform | Endpoint | Primary Param | Example |
|----------|----------|---------------|---------|
| Facebook ads search | `/v1/facebook/adLibrary/search/ads` | query | `running` |
| Facebook company ads | `/v1/facebook/adLibrary/company/ads` | pageId or companyName | `Lululemon` |
| Facebook ad detail | `/v1/facebook/adLibrary/ad` | id or url | `702369045530963` |
| Facebook find companies | `/v1/facebook/adLibrary/search/companies` | query | `Nike` |
| Google company ads | `/v1/google/company/ads` | domain or advertiser_id | `nike.com` |
| Google ad detail | `/v1/google/ad` | url | `https://adstransparency.google.com/...` |
| Google find advertisers | `/v1/google/adLibrary/advertisers/search` | query | `Nike` |
| LinkedIn ads search | `/v1/linkedin/ads/search` | company or keyword | `Shopify` |
| LinkedIn ad detail | `/v1/linkedin/ad` | url | `https://www.linkedin.com/ad/...` |
| Reddit ads search (not in combined spec) | `/v1/reddit/ads/search` | query | `gaming` |
| Reddit ad detail (not in combined spec) | `/v1/reddit/ad` | id | `t3_abc123` |

### Trending / Popular
| Content | Endpoint | Param | Example |
|---------|----------|-------|---------|
| Trending feed | `/v1/tiktok/get-trending-feed` | region (required) | `US` |
| Popular videos (not in combined spec) | `/v1/tiktok/videos/popular` | period, page, orderBy, countryCode | |
| Popular creators | `/v1/tiktok/creators/popular` | | |
| Popular songs (not in combined spec) | `/v1/tiktok/songs/popular` | page, timePeriod, rankType, newOnBoard, commercialMusic, countryCode | |
| Song details | `/v1/tiktok/song` | clipId | `7439295283975702544` |
| Videos using song | `/v1/tiktok/song/videos` | clipId | `7439295283975702544` |
| Trending shorts (YT) | `/v1/youtube/shorts/trending` | | |

### Followers / Following / Live (TikTok only)
| Type | Endpoint | Example |
|------|----------|---------|
| Following | `/v1/tiktok/user/following` | `handle=stoolpresidente` |
| Followers | `/v1/tiktok/user/followers` | `handle=stoolpresidente` |
| Audience demographics | `/v1/tiktok/user/audience` (26 credits!) | `handle=shakira` |
| Live stream | `/v1/tiktok/user/live` | `handle=thejustalex` |

### TikTok Shop
| Type | Endpoint | Primary Param | Example |
|------|----------|---------------|---------|
| Search products | `/v1/tiktok/shop/search` | query | `shoes` |
| Store products | `/v1/tiktok/shop/products` | url | `https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079` |
| Product detail | `/v1/tiktok/product` | url | `https://www.tiktok.com/shop/pdp/goli-ashwagandha-gummies.../1729587769570529799` |
| Product reviews | `/v1/tiktok/shop/product/reviews` | url or product_id | `1731578642912612516` |
| User showcase | `/v1/tiktok/user/showcase` | handle | `mrtiktokreviews` |

### Link-in-Bio / Other
| Service | Endpoint | Param | Example |
|---------|----------|-------|---------|
| Linktree | `/v1/linktree` | url | `https://linktr.ee/...` |
| Komi | `/v1/komi` | url | `https://komi.io/...` |
| Pillar | `/v1/pillar` | url | `https://pillar.io/...` |
| Linkbio | `/v1/linkbio` | url | `https://linkbio.co/...` |
| Linkme | `/v1/linkme` | url | `https://linkme.bio/...` |
| Amazon Shop | `/v1/amazon/shop` | url | `https://www.amazon.com/shop/...` |
| Instagram basic profile | `/v1/instagram/basic-profile` | userId | `314216` |
| Instagram embed HTML | `/v1/instagram/user/embed` | handle | `jane` |
| Age/Gender detect | `/v1/detect-age-gender` | url | `https://www.tiktok.com/@charlidamelio` |
| Find creator emails | `/v1/find-creator-emails` | platform, handle | `instagram` + `jane` |
| Find other-platform profiles | `/v1/find-social-profiles` | platform, handle | `tiktok` + `charlidamelio` |
| Credit balance | `/v1/account/credit-balance` | (none) | |

Contact capture uses `/v1/find-creator-emails` and vetting uses `/v1/find-social-profiles`. Their skills hold the rules for when to call them. The cost of each is in the table below.

## Credit Costs

Most endpoints cost **1 credit** per request, but most routes do not state a cost in the spec, so treat 1 as the default and check the per-endpoint spec. Last verified 2026-11-02 (https://docs.scrapecreators.com/openapi.json). Exceptions:

| Endpoint | Cost | Condition |
|----------|------|-----------|
| `/v1/tiktok/user/audience` | 26 credits | always (country only, no `cache_max_age`) |
| `/v1/tiktok/video/transcript` | 1 credit | native captions, only if a transcript is returned (0 if none) |
| `/v1/tiktok/video/transcript` | 1 credit flat | `use_ai_as_fallback=true`, successful AI transcript of 120 s or less |
| `/v1/tiktok/video/transcript` | 10 credits per started minute | `allow_long_transcription=true`, applies to ALL successful AI transcripts, even short ones |
| `/v1/google/company/ads` | 25 credits | `get_ad_details=true`, otherwise 1 |
| `/v1/find-creator-emails` | 10 credits if any email is returned, 1 if `emails` is empty | 0 on cache hit, invalid input, missing source profile or failed lookup |
| `/v1/find-social-profiles` | 10 credits | per successful live lookup, 0 on cache hit |
| `/v1/instagram/post`, `/v2/tiktok/video`, `/v1/truthsocial/post` | 10 credits | `download_media=true` and media found, otherwise 1 |
| `/v2/instagram/post/comments` | 1 credit per page with comments, 15 with `include_replies=true` | empty pages cost 0 |
| `/v1/instagram/profile` | 0 for age-gated 403 or "restricted/unavailable" 404 | legacy 200 "private/not found" placeholders cost 1 |

The same AI-transcript pricing applies to the dedicated routes `/v1/facebook/post/transcript`, `/v1/facebook/adLibrary/ad/transcript`, `/v1/twitter/tweet/transcript`, `/v2/instagram/media/transcript` and the Kick and Twitch clip transcripts. On detail routes (`/v1/facebook/adLibrary/ad`, and `/v1/tiktok/video` or `/v2/tiktok/video` with `get_transcript=true`) the flat 1 credit does not apply: short AI (120 s or less) is included in the base endpoint price with no extra AI fee, and long-mode AI is billed in addition to the base endpoint cost (Last verified 2026-11-02). Dedicated native-caption transcript routes (TikTok, YouTube, Reddit, Rumble, LinkedIn) cost 1 only when a transcript is returned, and `/v1/youtube/video/transcript` costs 1 and uses no AI. `/v1/instagram/search/profiles` states no cost in the spec, so assume 1 but treat it as unstated.

Caching: only 36 of the 197 spec paths accept `cache_max_age` (Last verified 2026-11-02). HypeStake's client lists 35 cacheable paths from its 2026-09 spec copy, and that copy has no `/v1/find-creator-emails`; the difference is unresolved, so re-count from the live spec before relying on either list (checked against HypeStake source 77a68e5c, 2026-11-10, see `../../references/hypestake-platform-map.md`). A cache hit costs 0 credits. Search, list and audience endpoints do not take it.

Check balance with `GET /v1/account/credit-balance` (the alias `/v1/credit-balance` also responds; `/v1/credit/balance` returns 404). Warn users before calling expensive endpoints.

## Pagination

Paginated endpoints return a cursor/token in the response. Pass it back as a query param to get the next page.

| Cursor Field | Used By |
|-------------|---------|
| `cursor` | TikTok comments/search/song videos, Instagram comments, Reddit subreddit search, Pinterest, Bluesky, Facebook reels/photos/posts/comments, TikTok Shop products/user showcase |
| `max_cursor` | TikTok profile videos |
| `min_time` | TikTok following/followers |
| `continuationToken` | YouTube (all paginated endpoints) |
| `after` | Reddit posts, Reddit search |
| `next_max_id` | Instagram posts, Truth Social posts |
| `max_id` | Instagram reels |
| `page` | TikTok popular/shop, Instagram reels search, LinkedIn company posts, TikTok Shop reviews |
| `paginationToken` | LinkedIn ads |

## Common Optional Params

- **`trim`** (boolean): reduces response payload size. Use when you only need key metrics.
- **`region`** (string): 2-letter country code for proxy location. Does NOT filter by region, it only routes the request through that country's proxy.

## Common Pitfalls

- **Handles**: pass without the `@` symbol. Use `charlidamelio` not `@charlidamelio`. Applies to TikTok, Instagram, Twitter, Threads, Bluesky, Snapchat, Twitch, Pinterest, Truth Social
- **YouTube handles**: pass without the `@` symbol. Use `ThePatMcAfeeShow` not `@ThePatMcAfeeShow`. You can also pass a channelId (e.g. `UC-9-kyTW8ZkZNDHQJ6FgpwQ`) or full URL instead
- **Hashtags**: pass without the `#` symbol. Use `fyp` not `#fyp`. Applies to TikTok and YouTube hashtag search endpoints
- **Twitter**: `/v1/twitter/user-tweets` returns ~100 most popular tweets, not chronological/latest
- **Threads**: only last 20-30 posts visible publicly (vendor pack, not re-checked)
- **Facebook posts**: only 3 posts per page (vendor pack, not re-checked)
- **Facebook group posts**: only 3 posts per page (vendor pack, not re-checked)
- **LinkedIn company posts**: max 7 pages (corroborated by HypeStake's docs, checked against HypeStake source 77a68e5c, 2026-11-10)
- **Instagram play counts**: the vendor pack says these are Instagram-only views that exclude cross-posted Facebook views. Unverified: no check confirms that the ScrapeCreators field has this definition. Meta's own Business Discovery `view_count` has combined Instagram and Facebook views for crossposted video since April 2026 (Last verified 2026-11-02), so test one crossposted reel before comparing view baselines
- **Truth Social**: only prominent users (Trump, Vance, etc.) work publicly (vendor pack, not re-checked)
- **Instagram song reels**: deprecated, the endpoint exists but is non-functional (vendor pack, not re-checked)
- **Instagram profile search** (`/v1/instagram/search/profiles`): takes only `query`, has no pagination, and enriches only the first 10 accounts (bio, links, counts). The rest return id, username, full name, verified flag, photo and URL. It does not search Google-indexed bios or captions
- **Retired path**: `/v1/tiktok/hashtags/popular` was retired 2026-07-16 per the docs, with no replacement. It still returns 401 without a key (Last verified 2026-11-02), so it looks live but should not be used. Use `/v1/tiktok/search/hashtag` for hashtag-led discovery
- **Wrong paths return 404**: `/v1/youtube/channel/videos`, `/v1/twitter/user/tweets`, `/v1/instagram/basic/profile`, `/v1/detect/age-gender` and `/v1/credit/balance` do not exist (Last verified 2026-11-02)
- **Zero counts in search results**: search endpoints return cut-down account objects, and the spec's search examples zero-fill counts (the keyword-search example `aweme_count` and `following_count`, the hashtag-search example `follower_count` too). HypeStake reads a 0 from its Instagram profile, TikTok user and TikTok keyword search lanes as unknown; do the same and take counts from a profile call. Whether live responses zero-fill is not established (checked against HypeStake source 77a68e5c, 2026-11-10)
- **Hidden Instagram counts**: a timeline node with `like_and_view_counts_disabled: true`, or a like count of 0 on a post with comments, has unknown likes and views, never 0 (checked against HypeStake source 77a68e5c, 2026-11-10)
- **TikTok audience**: `audienceLocations[]` only (country, countryCode, count, percentage). No age or gender
- **Email fields**: `trim=true` drops `business_email` and `business_phone_number` from Instagram profile responses. Whether Instagram returns them at all is Unverified (a third-party pack (unlicensed) reports them null in its samples, not re-measured), so test a small sample first and use `/v1/find-creator-emails` if they come back empty
- **Transcripts**: the 120-second cap applies only to AI transcription and lifts with `allow_long_transcription=true` (10 credits per started minute). TikTok native captions have no fixed length limit, and `/v1/youtube/video/transcript` accepts any length when YouTube exposes public captions
- **Reddit subreddit names**: case-sensitive. Use "AskReddit" not "askreddit" (vendor pack, not re-checked)
- **No endpoint** (Last verified 2026-11-02, combined spec): Substack and Patreon (the strings appear only inside sample payloads), X user search (X has post search at `/v1/twitter/search/posts`), and any Bluesky search (Bluesky has `/v1/bluesky/profile`, `/v1/bluesky/user/posts` and `/v1/bluesky/post` only)
