# Creator scoring rubric

Rubric version 1.0, written 2026-11-02. This file is the detail behind `../skills/creator-vetting/SKILL.md`. It describes how an agent turns public evidence into the inputs of `../scripts/creator_score.py`, which computes the verdict.

**Evidence labels.** Verified = read at a primary page or the live API on 2026-11-02. Reported = taken from a summary, a secondary source or research notes and not re-checked. Unverified = judgment or a vendor claim with no public method. Judgment default = a number chosen by the authors of this rubric, not measured. Every weight, threshold and cutoff in this file is a judgment default unless it says otherwise, because no public study supplies them. Calibrate them against deal outcomes (section 9) before treating the score as predictive.

## 1. Contract with creator_score.py

The module is stdlib-only and tested (`../scripts/tests/test_creator_score.py`). Do not edit it from a vetting run. If this file and the module disagree, the module wins and this file is a bug. `../src/creator-score.ts` is a TypeScript port that must match it on every vector in `../vectors/creator-score.vectors.json`. The score is not HypeStake's Match Score: it is one creator against one research brief, not a Creator and Brand pair.

| Constant | Value | Meaning |
|---|---|---|
| `WEIGHTS` | niche_fit 20, audience_fit 15, engagement_quality 15, authenticity 15, reach 10, brand_safety 10, sponsor_readiness 10, contactability 5 | Sum is 100. Judgment defaults. |
| `GATES` | G1 to G5 (section 2) | Any gate returns `verdict: reject` and `score: null`. |
| `CONFIDENCE_RANK` | low 0, medium 1, high 2 | The only legal confidence values. |
| `BAND` | high 5, medium 10, low 20 | Fixed points shown either side of the score, clipped to 0 and 100. It is a display band, not a statistical interval. |
| `MIN_POST_AGE_HOURS` | 72 | Younger posts are dropped from the baseline. YouTube needs 336 (section 4). |
| `FLOORS` | authenticity 40, brand_safety 50 | A present dimension scoring below its floor caps the total. |
| `FLOOR_CAP` | 60 | The cap applies only when the total is above 60. `floor_capped_by` lists the dimension even when the total was already 60 or less. |
| `baseline_confidence(n)` | n >= 20 high, n >= 12 medium, else low | Applied to settled posts. |
| Outlier labels | lift >= 5 huge, >= 2 strong, >= 1.5 mild | Lift is post metric divided by the median of settled posts. |

Behaviours that matter when you build a payload:

- **Renormalisation.** Dimensions with `score: null` (or left out) are dropped and the remaining weights are rescaled to 100. The total is never zero-filled. `weights_used` shows the rescaled weights.
- **Overall confidence** is the lowest confidence among present dimensions, and is forced to `low` when any dimension is missing. Expect `low` for most public-only vetting. That outcome is correct, and it widens the band to plus or minus 20.
- **No dimension present** returns reject with G3.
- **Invalid input raises `ValueError`:** unknown dimension name, score outside 0 to 100, confidence other than low, medium or high, unknown gate code. There is no "none" confidence: use `score: null` instead.
- **Posts with a null metric or no `age_hours` are excluded** from the baseline and counted separately (`excluded_missing_metric`, `excluded_unknown_age`), because an unknown age is not a settled one. Always supply `age_hours`.
- **Baseline of 0** gives `lift: null` for every post.
- The command line takes `min_age_hours` in the input. For YouTube pass 336.
- **Invalid input raises** for posts too: a negative, boolean or non-numeric metric or age, a metric named `id`, `lift`, `label`, `__proto__`, `constructor` or `prototype`, and an id that is not a string, null or a whole number of at most 2**53 - 1. Pass larger platform ids (Instagram, TikTok and X ids often are) as strings, so they survive JSON and JavaScript unchanged.

Usage from this file's folder (`references/`):

```bash
# Dimensions and gates in, verdict out
python3 -I -B ../scripts/creator_score.py < vet.json
# {"dimensions": {"reach": {"score": 60, "confidence": "high", "evidence": "median 41k views, n=22"}, ...},
#  "gates": []}

# Posts in, baseline and lift per post out (one platform, one format, one metric per call)
python3 -I -B ../scripts/creator_score.py < posts.json
# {"metric": "views", "posts": [{"id": "a", "views": 1000, "age_hours": 200}, ...]}
```

Worked example (run on 2026-11-02): seven dimensions scored, `audience_fit` null. Inputs: niche 82 high, engagement 68 medium, authenticity 72 medium, reach 60 high, brand safety 90 medium, sponsor readiness 70 medium, contactability 100 high. Output: score 75.8, band 55.8 to 95.8, confidence low, missing `["audience_fit"]`, niche_fit reweighted from 20 to 23.5. Hand check: (82x20 + 68x15 + 72x15 + 60x10 + 90x10 + 70x10 + 100x5) / 85 = 75.76. A second run with authenticity 35 and three other dimensions present returned a total of 60 with `floor_capped_by: ["authenticity"]`.

## 2. Gates

Evaluate gates before scoring. A gate is a veto, so a high score elsewhere cannot offset it. Show the gate, its reason and the evidence link in the report, and say "insufficient data" for G3 rather than "low score". Trigger thresholds below are judgment defaults.

| Gate | Module text | Trigger rule | Does not trigger it |
|---|---|---|---|
| G1 | brand-safety floor hit | A post, caption, transcript or comment by the creator falls in a category the brand configured as a floor, dated within the last 12 months, with a post URL as evidence. | A medium or high tier hit below the brand's floor (that lowers `brand_safety`). Third-party comments on a post. |
| G2 | strong evidence of inauthentic audience or engagement | Documented purchased followers or views, an engagement-pod pattern visible on at least 5 of the last 10 posts, or a platform or regulator action. | Any single ratio, any vendor "fake follower" figure, a follower spike without a second signal. |
| G3 | insufficient public data to score | Fewer than 10 public posts in 90 days on the scored platform, or a private or age-gated account (Instagram Business Discovery returns no data for age-gated professional accounts, Last verified 2026-11-02). The module also returns G3 when no dimension is scorable. | A single missing dimension (renormalise instead). |
| G4 | identity unverifiable (profile, site and handle do not agree) | The profile cannot be tied to a stable named person or business: the bio link, creator-owned site and same-handle accounts on other platforms disagree or do not exist. Impersonation risk. | A creator who is anonymous by choice but consistent across surfaces (record as a caveat, brand decides). |
| G5 | persistent undisclosed sponsored content | At least 3 sponsored-looking posts in the last 20 with no disclosure that meets section 8. | One missed disclosure. Absence of a platform flag alone (flags are creator-set). |

A gate reject sets the record's status to `gated:G#`, using the lowest code that fired (status vocabulary in `../skills/creator-research/SKILL.md`).

The module treats G5 as a reject. The methodology notes suggested a review gate because it is a judgment call. Report G5 as "reject, compliance risk" and allow a human to override: re-run without G5, and record the reviewer and reason in the transparency record.

Brand-specific exclusions (direct-competitor exclusivity, market mismatch, banned categories) are not module gates and cannot be passed as gate codes. Drop the creator before scoring, state the reason in the report, and do not invent a G6.

## 3. Dimensions

Common rules for every dimension:

- Give a score from 0 to 100, or `null` when public data cannot support one. Never fill with 0 or 50.
- Give a confidence of low, medium or high and a one-line `evidence` string (counts, window, cohort).
- Use each piece of evidence in one dimension only. The same comments may be read twice, but a penalty is taken once.
- Instagram `like_count` of 0 and an omitted `like_count` both mean hidden or unknown (the 2021 changelog says an indirect query returns 0, the current reference says the field is omitted, and the owner can also hide comments, views and shares; Last verified 2026-11-02). Set the value to null, never to zero engagement.
- Score one platform and one format at a time. Combine platforms only by scoring each and stating which one the deal covers.

### 3.1 Niche fit (weight 20)

- **Evidence.** Captions, hashtags, on-screen text and transcripts of the last 20 posts on the scored platform (minimum 12), past sponsor categories, and the brief (topics, exclusions, product category).
- **Conversion.** Classify each post against the brief: on-topic 1, adjacent 0.5, off-topic 0. Score is 100 times the mean. Quote the post URL for each on-topic and off-topic example.
- **Defensible.** Topic, format and series are directly observable. Hashtags count only when the caption or transcript agrees.
- **Not defensible.** Inferring niche from handle, name or follower count. Treating one viral post as the niche. Hashtag lists with no matching content.
- **Confidence.** High with 20 or more posts classified from captions or transcripts. Medium with 12 to 19 posts, or captions only on a video-first platform. Low below 12 (in practice G3 or a null score).

### 3.2 Audience fit (weight 15)

- **Evidence.** Three observable checks against the brief's target market:
  1. Creator-declared location and language (bio, profile fields, caption language). This describes the creator, not the audience.
  2. Commenter language label on the last 10 posts, from the `comment-mining` authenticity mode. Coarse proxy only, because a comment is a small, self-selected, bot-contaminated sample and language is not country.
  3. Topic overlap between what commenters ask about and the product category.
  Optional fourth, supporting only: TikTok `/v1/tiktok/user/audience` (26 credits, `handle` only, country list only, no age or gender, no `cache_max_age`; Last verified 2026-11-02). Its data source and method are not stated, so treat it as unverified third-party data. CreatorDB returns gender ratio and age bands for TikTok, but its page was summariser-read and not re-checked, its method is not stated and its pay-as-you-go price was not confirmed (Last verified 2026-11-02).
- **Conversion.** Rate each available check match 100, partial 50, mismatch 0. Score is the mean of the available checks. With fewer than two checks, set `null`. Report commenter language as a label ("mostly English, some Spanish"), never as a percentage of the audience.
- **Defensible.** Creator-declared market, caption language, comment-language label, topic overlap, collaboration graph.
- **Not defensible.** Audience age, gender, income or country percentages from public data. Any precise split from a scraped or modelled source. Inferring silent followers from commenters. Using a country list as a gate. Creator location as audience location (expats, global niches, travel).
- **Confidence.** Low by default. Medium when at least two checks agree and at least 100 classifiable comments across at least 5 posts back them. High only with first-party analytics the creator connected (OAuth insights). A media-kit audience screenshot is stored as "creator-supplied, unverified" and raises confidence to medium at most.

### 3.3 Engagement quality (weight 15)

- **Evidence.** Likes, comments, views and followers per settled post, one format at a time, plus the `outlier_report` output and the substantive share from the `comment-mining` authenticity mode.
- **Conversion.**
  1. Choose `er_basis`: views where view counts are public (TikTok, YouTube, Reels), followers otherwise. ER per post is (likes + comments) divided by that basis. Shares and saves are not public on most platforms, so leave them out and say so.
  2. Take the median over settled posts. Store `er_basis`, `stat` (median), `n_posts` and the post-age cutoff with the value.
  3. Score the percentile of that median within the cohort: same platform, same follower tier, same format, same `er_basis`, same median statistic. A cohort needs at least 30 creators (judgment). Percentile 50 scores 50, so a typical creator lands near 50.
  4. Add up to 10 points when questions, specifics or buying intent make up at least 20% of non-spam comments (judgment). Generic-comment share goes to authenticity, not here.
  5. Cold start (cohort under 30): compare to the prior in section 5 only when platform, basis, statistic and numerator match. Section 5 states each prior's numerator, and a prior whose numerator is not (likes + comments) can only be read as a rough guide. With ratio r = creator median over prior median: r < 0.5 scores 20, 0.5 to 0.8 scores 40, 0.8 to 1.25 scores 55, 1.25 to 2 scores 70, above 2 scores 85, all at low confidence. A ratio above 2 is also an authenticity prompt, not just a reward. No verified views-basis prior exists here: rank within the shortlist at low confidence, or return `null` when the shortlist is under 10.
- **Informational flag.** If more than a third of settled posts label strong or huge, the baseline is unstable: split by format and recompute before scoring.
- **Defensible.** Median ER with its basis stated, percentile within a like-for-like cohort.
- **Not defensible.** Comparing ER across bases or across mean and median. Reading hidden-like zeros as low engagement. Fixed "good ER" tiers. Pooling formats (carousel, image and Reel differ in the vendor data). Treating a benchmark as a target.
- **Confidence.** `baseline_confidence(n)` on settled posts, capped at medium. Low whenever only a cold-start prior is available.

### 3.4 Authenticity (weight 15)

Authenticity is scored as the inverse of risk, from independent weak flags. The output class is low, elevated, high or insufficient-data. Never output "X% fake followers".

- **Evidence (each flag recorded with a link).** F1 and F2 come from the per-post counts that the `comment-mining` authenticity mode returns before it filters anything.
  - F1. Generic or pod-style comments ("nice pic", "wow", emoji only) on at least 3 of the last 10 posts.
  - F2. Spam, scam-link or bot-like comment clusters on at least 3 of the last 10 posts.
  - F3. Views-to-followers (or median views) below the 10th percentile of the same-platform, same-tier cohort. Report as "unusual".
  - F4. Follower jump with no matching post or news event. Needs HypeStake's own snapshots over time, so it is unavailable on a first look. A spike can also be legitimate virality.
  Thresholds in F1 to F4 are judgment defaults.
- **Conversion.** At least 3 of the 4 signal types must be checkable, with at least 100 comments across at least 5 posts for F1 and F2. Otherwise set `null`. Then: 0 flags scores 90, 1 flag 70, 2 flags 50, 3 or more flags 30. Classes: 0 is low risk, 1 to 2 elevated, 3 or more high. A score of 30 sits below the floor of 40 and caps the total at 60.
- **Gate boundary.** Documented purchases, a pattern on 5 of 10 posts, or a platform or regulator action goes to G2, not here.
- **Defensible.** A list of explainable flags with links, labelled "risk signal, not proof".
- **Not defensible.** A "% fake" or "authenticity %" figure. Any single flag as proof. The Socialbakers 50:1 following-to-followers rule as a detector: on 2013 bought Twitter followers it had precision 0.997 but recall 0.162, so it catches only crude fakes (Cresci et al. 2015, Verified, Last verified 2026-11-02). The creator's own follow ratio as a score input (no study gives a threshold, Unverified). Vendor accuracy claims such as "95.5%" (HypeAuditor claims it, with no public ground truth, Unverified).
- **Why caution.** Published detectors are tested on purchased or hand-labelled sets that are easier than current fakes. Supervised bot classifiers deteriorate on bot types missing from training, and an ensemble improved F1 on unseen accounts by 56% on average (Sayyadiharikandeh et al. 2020, abstract only, Reported). Pod comments lean generic (Weerasinghe et al. 2020, Reported). Treat every flag as a prompt for a human look.
- **Legal frame (Last verified 2026-11-02).** 16 CFR 465.8 makes it a violation to buy, procure, sell or distribute fake social-media influence indicators that the person knew or should have known were fake and that materially misrepresent influence for a commercial purpose. Effective 2024-10-21. FTC staff say hiring an influencer who happens to have fake followers is not by itself liability, but red flags a brand ignored bear on "should have known". Record the flags seen and when. This is not legal advice.
- **Confidence.** Capped at medium. Medium needs all of the minimums above plus 12 or more settled posts. Low otherwise. High only when first-party analytics the creator connected reconcile with public counts.

### 3.5 Reach (weight 10)

- **Evidence.** Median views of settled posts in the deal's format (from `outlier_report`), followers as a secondary figure.
- **Conversion.** If the brief gives a target median-views range, score 100 inside it, 60 within a factor of two outside it, 20 beyond (judgment). Otherwise score the percentile of median views within the same-platform, same-format cohort, and say which cohort.
- **Defensible.** Public view counts on settled posts, median not mean.
- **Not defensible.** Followers alone as reach. Pooling platforms. Views windows that cross a definition change: Meta's Business Discovery `view_count` combines Instagram and Facebook views for crossposted video since April 2026, and YouTube `viewCount` counts playback starts including autoplay and hover from 2026-08-24 (both Last verified 2026-11-02). Such baselines are not like-for-like.
- **Confidence.** `baseline_confidence(n)` on settled posts.

### 3.6 Brand safety (weight 10)

- **Evidence.** The scan in section 7, per category tier: none, low, medium, high, floor.
- **Conversion.** Start at 100. Subtract per category, using the highest tier found: low 5, medium 15, high 35 (judgment defaults). A brand may mark a category as tolerated up to a tier, which zeroes penalties through that tier. A floor-tier hit in the last 12 months is G1, not a penalty. Clip at 0. Two high hits give 30, below the floor of 50, so the total is capped at 60.
- **Defensible.** Dated, linked evidence per hit and the count of posts scanned.
- **Not defensible.** A clean result from fewer than 20 posts or without the comment scan. Treating absent controversy search results as proof of safety. Using thresholds that the brand did not set.
- **Confidence.** Medium for text classification of 20 or more posts plus comments on 10 posts. Low for fewer posts, or when image or video-frame classification carries a hit (flag for human review). High only after a person reviewed every flagged item.

### 3.7 Sponsor readiness (weight 10)

- **Evidence.** Disclosure habits on sponsored-looking posts (section 8), delivery consistency, and business-ready signals.
- **Conversion.** Three parts, each 0 to 100:
  - Disclosure compliance, weight 50: share of sponsored-looking posts with a compliant disclosure. Needs at least 3 such posts, otherwise unknown.
  - Delivery consistency, weight 25: fortnights with at least one post, out of the last six, divided by six.
  - Business-ready signals, weight 25: media kit or rate card link, business-inquiries contact, talent-manager listing, prior tagged brand partnership with disclosure. Score is signals found out of four.
  If disclosure compliance is unknown, renormalise over the other two and cap confidence at low. Predictive value of the business-ready signals is Unverified, so they carry observable weight only. A pricing or "work with me" phrase on its own is weak evidence, because creators who sell products have the same pages. Prefer structural evidence such as a media kit file or a tagged partnership.
- **Sponsor saturation.** Share of the last 20 posts that are sponsored-looking. Report it as a flag. No study links it to audience trust (Unverified), so it carries no penalty until calibrated.
- **Defensible.** Counted, linked disclosures and gaps.
- **Not defensible.** Reading missing platform flags as "not sponsored". A single vendor figure that over half of one day's #ad Instagram engagements were fake (Reported, one day, vendor data) is a reason to cross-check, not a rate.
- **Confidence.** Medium with at least 3 sponsored-looking posts evaluated and 12 or more posts overall. Low otherwise.

### 3.8 Contactability (weight 5)

- **Evidence.** The record's `contact_tier`, set by `creator-contact-capture` from what the creator published on a creator-owned surface (bio, link-in-bio, site). Capture belongs to that skill, and any use of the contact to `outreach-compliance`.
- **Conversion.** Map the tier: `email`, `business_inbox` or `form` scores 100. `manager_listing` (a manager or agency named, no address for the creator) scores 70. `dm_only` scores 40. `none` scores 0, which is an observation after bio, link-in-bio and site were checked and not missing data. A record with no `contact_tier` means capture did not run, so set `null`.
- **Defensible.** Direct observation of what the creator chose to publish.
- **Not defensible.** Guessed or pattern-built addresses. Treating a scraped personal address as a business contact.
- **Confidence.** High when each surface was checked. Medium when the site or link-in-bio could not be loaded. If a tier of `none` came from a source skipped by the route check, say so in the evidence string and set medium at most.

## 4. Baselines, post age and formats

- **Median, not mean,** so one viral post does not hide itself (a test in the module). Score one platform and one format at a time: Reel, carousel, image, Short, long video, livestream. Exclude pinned posts and paid-partnership posts from the organic baseline, and compare sponsored to organic only with at least 5 sponsored posts (judgment).
- **Sample size.** The module's note that a 10-post median can be off by 1.5 to 1.8 times comes from a simulation with independent log-normal views (Computed, assumption: views are independent, which they are not). The 80% interval of the ratio of sample median to true median:

  | n posts | spread 0.8 | spread 1.2 |
  |---|---|---|
  | 6 | 0.64 to 1.64 | 0.51 to 2.14 |
  | 10 | 0.69 to 1.48 | 0.58 to 1.83 |
  | 12 | 0.71 to 1.43 | 0.60 to 1.71 |
  | 20 | 0.76 to 1.32 | 0.66 to 1.52 |
  | 30 | 0.80 to 1.26 | 0.71 to 1.41 |

  So a "2x median" outlier on 10 posts is weak evidence. The module uses 12 for medium and 20 for high. The `outlier-post-finder` skill says low under 10 posts: inside vetting use the module's stricter cutoffs.
- **Post age.** On Facebook and Instagram, about half of interactions arrive within 4 and 2 hours, most posts live 20 to 50 hours, and early interactions predict later popularity (ASONAM 2021, 651 Italian influencers, about 4M posts, 2016 to 2021; Last verified 2026-11-02). That study covers Facebook and Instagram only, so it supports a cutoff of about 72 hours for Instagram (and Facebook). The 72-hour cutoff for TikTok and the 336-hour cutoff for YouTube are judgment defaults, because blog claims about TikTok and YouTube post lifetimes are Reported and inconsistent.
- **Definition drift.** Re-pull the baseline when a platform changes a metric. Known changes are in 3.5.

## 5. Cold-start priors (vendor-sourced, dated)

Use these only until HypeStake has its own cohorts, and say "vendor prior" next to any number you cite. They are brand-account samples, not random creator samples, and engagement fell sharply year over year, so they age fast. Treat any prior as stale after about 12 months (judgment). Re-derive cohort medians from scraped creators every quarter and retire a prior once its cohort has 30 or more creators.

| Source and date | Metric and basis | Values | Caveat |
|---|---|---|---|
| Rival IQ 2025 Social Media Industry Benchmark Report, CY2024 data (Last verified 2026-11-02) | Median ER by follower, all industries. Numerator: "all these interactions" as the report defines them; shares and saves are not confirmed as excluded | Instagram 0.36% per post, TikTok 1.73% per video, Facebook 0.046%, X 0.015% | 150 random companies per industry, each with at least 5,000 followers on Instagram, TikTok and X as of Jan 2025 (Facebook 25k to 1M fans). Numerator may differ from likes + comments |
| Same report, "Influencers" industry row | Median ER by follower | Instagram 0.576%, TikTok 1.11%, Facebook 0.095%, X 0.021%; 4.50 Instagram posts per week, 1.99 TikTok videos per week | One of 14 industries, brand accounts, not a random creator sample. Same numerator caveat |
| Same report, key takeaway | Year-over-year change in engagement | Facebook -36%, Instagram -16%, TikTok -34%, X -48% | Shows how quickly priors age |
| Socialinsider Instagram benchmarks, 2025 (Reported, research notes, not re-checked) | Mean ER by follower | 0.48% overall (0.50% in 2024); Reels 0.52%, carousel 0.55%, image 0.37% | Mean not median, business accounts 1K to 1M, page has an unexplained 0.45% elsewhere. Numerator not stated |

Not used: Favikon tier figures (formula, statistic and sample counts unstated or contradictory), Influencer Marketing Hub tier ranges (appear only in third-party blogs that disagree), HypeAuditor reports (gated, Unverified). Socialinsider's TikTok by-views tiers were read from a page that contradicts itself, so no TikTok views-basis prior is carried.

## 6. Authenticity evidence base

| Study | Finding | Status |
|---|---|---|
| Cresci et al., "Fame for sale", 2015 | On 1,950 humans and 1,950 bought Twitter fakes (bought 2013): Socialbakers 50:1 rule precision 0.997, recall 0.162; Camisani-Calzolari precision 0.974, recall 0.062; Stateofsearch 100:1 precision 0.541, recall 1.0 | Verified (Last verified 2026-11-02) |
| Akyon and Kalfaoglu, arXiv 1910.03090 | Small public Instagram datasets, reported accuracy 96% (fake) and 86% (automated), with follower-count features the authors flag as biased | Research notes, not re-checked |
| Sayyadiharikandeh et al., CIKM 2020 | Classifiers degrade on unseen bot types | Research notes, abstract only |
| Weerasinghe et al., WWW 2020 | Pod-boosted posts detectable (AUC 0.91 to 0.94), comments lean generic | Reported |

No public study gives a threshold for comment-to-like ratio, an engagement-versus-size curve, view-to-follower ratio or growth-spike precision. Use them only as within-cohort percentiles worded as "unusual".

## 7. Brand-safety scan checklist

**Status of GARM (Last verified 2026-11-02).** The World Federation of Advertisers announced on 9 August 2024 that GARM "will discontinue its activities" and named no successor. It named the Brand Safety Floor and the Adjacency Standards Framework as GARM tools. Use 9 August 2024 as the date; an 8 August date is Unverified. Vendors still sell GARM-style tiers and responsibility has moved to each advertiser (Reported). So the category list below is a vocabulary, not a current standard, and thresholds must be per-brand configurable.

**Category scaffold (Unverified, recalled from the GARM taxonomy, verify before shipping).** Adult and explicit sexual content; arms and ammunition; crime and harmful acts, human-rights violations; death, injury or military conflict; online piracy; hate speech and acts of aggression; obscenity and profanity; illegal drugs, tobacco, vaping, alcohol; spam or harmful content; terrorism; debated sensitive social issues; misinformation.

Store the brand's configuration with the run:

```json
{"floor_categories": ["hate_speech", "terrorism"],
 "tolerated_up_to": {"obscenity_profanity": "medium", "alcohol": "low"},
 "excluded_competitors": [], "market": "US"}
```

Checklist:

1. Last 20 to 30 posts per platform (or 90 days, whichever gives more): caption, on-screen text or transcript, hashtags, thumbnails or frames. Tier each category and record the post URL for every hit.
2. Comments on the last 10 posts: slurs, harassment, scam or spam links, pod-style generic comments (these also feed F1 and F2, counted once).
3. Controversy: news and search hits for the creator name with "lawsuit", "scam", "apology", "cancelled". Past brand-partner removals if public.
4. Disclosure compliance on sponsored-looking posts (section 8).
5. Competitor and category conflicts: recent paid promotion for direct competitors, exclusivity risk.
6. Account integrity: handle changes, bio claims against evidence. Deleted-post history is not public (Unverified).

Output per category: tier, evidence links, `n_posts_scanned`, confidence. Image and video classification is low to medium and carries a human-review flag.

## 8. Disclosure compliance checklist (Last verified 2026-11-02)

Source: FTC "Disclosures 101 for Social Media Influencers" (page dated November 2019).

- The disclosure must be hard to miss and placed with the endorsement. Terms like "ad", "advertisement" and "sponsored" are adequate. Vague terms such as "sp", "spon" or "collab", and stand-alone "thanks" or "ambassador", are not.
- A platform's disclosure tool alone is not assumed to be enough. In video, the disclosure should be in the video, not only the description. Anything behind a "MORE" click is likely missed. A hashtag such as #ad is fine but not necessary, and must not be buried in a group of hashtags or links.
- Platform flags are creator-set, so absence proves nothing. YouTube `videos.list` accepts `part=paidProductPlacementDetails` with `hasPaidProductPlacement`, but whether an API key alone can read it is Unverified: make one live call first. Instagram's "Paid partnership" label can be written through the Content Publishing API (April 2026) but no read field is documented, and scrapeability from the public page is Unverified. TikTok's Commercial Content API covers EEA countries only and its eligibility for HypeStake is Unverified, likely unavailable.
- Caption fallback to find sponsored-looking posts: #ad, #sponsored, "paid partnership", "in partnership with", discount codes, affiliate links, brand @-tags.

## 9. Calibration plan

The weights and thresholds are judgment until outcomes say otherwise. HypeStake needs this data before replacing them:

| Data | Why |
|---|---|
| Outcome per deal: creator replied, accepted, signed, posted on time, disclosure compliant, brand-rated fit, delivered views or clicks against price paid, repeat engagement, dispute | These are the labels |
| Time-stamped pre-deal snapshot of every feature the vetter saw, plus rubric version, cohort and deal terms | Without it, features leak the outcome |
| Brand-reported fraud or non-performing outcomes | Ground truth for each authenticity flag, which the literature lacks |
| Creator-connected first-party analytics | Measures the error of the public proxies in 3.2 and 3.4 |
| Rejected and unscored creators, logged with reason | Outcomes exist only for signed deals, so models trained on signed deals alone are biased |

Method once enough deals exist (no minimum count has been derived, Unverified, so decide from the observed base rate):

1. Report outcome rate by score decile and by dimension, per platform and tier.
2. Fit a regularised logistic or ordered model on the eight dimension scores and compare coefficients to the judgment weights.
3. Calibrate (isotonic or Platt) so that a score of 72 maps to an observed success rate.
4. Keep gates rule-based so a model cannot override a safety floor.
5. Re-derive cohort medians quarterly and retire vendor priors.
6. Where a brand agrees, hold out a small set of near-threshold creators to reduce selection bias.

## 10. Transparency record

Ship every score with this record:

```json
{"rubric_version": "1.0", "collected_at": "2026-11-02T00:00:00Z", "platform": "instagram", "format": "reel",
 "er_basis": "views", "stat": "median", "n_posts": 22, "post_age_cutoff_hours": 72,
 "cohort": "instagram/reel/10k-100k/n=41", "brand_config": "brand-safety.json",
 "dimensions": {"reach": {"score": 60, "confidence": "high", "evidence": "median 41k views, n=22"}},
 "flags": [{"id": "F1", "post": "https://...", "note": "generic comments"}],
 "gates": [], "overrides": []}
```

Add a "what would raise confidence" line: connect first-party insights, add months of snapshots, review flagged frames.

## 11. Unverified and open

Unverified: HypeAuditor accuracy claims; YouTube `paidProductPlacementDetails` readability with an API key; whether the Instagram partnership label is scrapeable; TikTok Commercial Content API eligibility; the GARM category list; the 8 August 2024 GARM date; predictive value of media kits and sponsor saturation; any minimum calibration sample size. All numeric thresholds in sections 2 and 3 are judgment defaults.
