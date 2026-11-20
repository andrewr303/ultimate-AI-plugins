# Creator vetting methodology from public data (research notes, 2026-11-02)

Label key. **Confirmed** = I read it at the cited URL in this session. **Reported** = seen only in a search-result summary, a secondary source, or a page I could not open; do not treat as verified. **Unverified** = my judgment, memory, or a vendor claim with no method disclosed.
"Computed" = my own calculation, with its assumption stated. Nothing in section 7 is a research result; it is design judgment.

## 1. Engagement-rate definitions and benchmarks

### Formulas (what can be computed from public data)
| Name | Formula | Public-only? | Status |
|---|---|---|---|
| ER by followers (ERF) | (likes + comments [+ shares + saves]) / followers, per post, then median or mean over posts | Yes (likes/comments/followers). Shares/saves are not public on most platforms. | Confirmed: Rival IQ PDF and Socialinsider pages |
| ER by views (ERV) | engagements / views of that post | Yes where view counts are public (TikTok, YouTube, IG Reels via `view_count`) | Confirmed: Socialinsider TikTok page |
| ER by reach / impressions | engagements / reach (or impressions) | No. Needs owner analytics. | Reported (Emplifi moved brand benchmarks to a per-impression metric; not read in full) |

- Rival IQ: "Engagement rate is calculated based on all these interactions divided by total follower count"; median across 150 randomly chosen companies per industry. Confirmed. Source: https://get.rivaliq.com/hubfs/eBooks/2025-Social-Media-Industry-Benchmark-Report.pdf (downloaded, `pdftotext`).
- Socialinsider IG: (likes + comments) / followers x 100, averaged across posts. TikTok on its blog is by views (sum of likes, comments, shares, saves / views). Its general benchmarks page uses followers for TikTok and states that its TikTok benchmark report is by views. Confirmed. Sources: https://www.socialinsider.io/social-media-benchmarks, https://www.socialinsider.io/blog/tiktok-benchmarks/, https://www.socialinsider.io/blog/instagram-benchmarks/
- Consequence: a number is only comparable to a benchmark with the same denominator and the same central statistic (median vs mean). Store `er_basis` ("followers" or "views"), `stat` and `n_posts` with every ER value. (Design judgment.)

### Benchmarks with named dataset and date (3-5 usable numbers)
1. **Rival IQ 2025 report (data for calendar 2024), ERF, median per account, brand accounts**: Instagram all-industry median **0.36%**; TikTok **1.73%**; Facebook 0.046%; Twitter 0.015%. Confirmed (PDF pp. per-platform pages). Sample is 150 random companies per industry, each with >=5,000 followers on IG/TikTok/Twitter and Facebook fans of 25k-1M as of Jan 2025. That is a size-filtered sample of brand accounts, so it is not a creator sample.
2. **Rival IQ 2025, "Influencers" industry row** (same method): IG **0.576%**, TikTok **1.11%**, Facebook 0.095%, Twitter 0.021% per post/video. Confirmed. Best creator-flavoured ERF figure I could verify at a named source. IG posts per week 4.50, TikTok videos per week 1.99.
3. **Socialinsider TikTok, ERV, brand accounts 1K-1M followers, 40.7M videos, organic, 2025 values** (page labels them 2026), by follower tier: <5K **4.40%**; 5K-10K 4.00%; 10K-50K 3.90%; 50K-100K 3.75%; 100K+ 3.95%. Confirmed on page, but the page is internally inconsistent: tier labels vs methodology text, and a platform-wide 3.85%/4.20% that matches none of the tier rows. These are means ("averaged"), not medians. Vendor-sourced. It shows a very flat size curve on TikTok by views.
4. **Socialinsider Instagram, ERF, 67.5M posts, business accounts 1K-1M, 2025**: overall **0.48%** (0.50% in 2024); Reels 0.52%, carousel 0.55%, image 0.37%. No ER-by-tier table on the page. Confirmed on page, with an unexplained 0.45% elsewhere on it. Vendor-sourced, mean.
5. **Favikon 2025 engagement benchmark (blog, dated 2025-07-28)**: IG nano (0-10K) top-quartile "3.4%+"; mega (500K+) "1.8%+". Confirmed that the page says this. The page states no formula, no central statistic and no date range, and its own sample counts conflict (6M vs 8.3M profiles). Treat as Reported-quality and vendor-sourced. I did not find a usable tier table from Influencer Marketing Hub or HypeAuditor: IMH tier ranges (nano 5-8%, micro 2-4%, mega 0.5-1%) appear only in third-party blogs that disagree with each other, so Reported, not used. The HypeAuditor 2025/2026 reports are gated; Unverified.

### How fast they age
- Year-over-year change is large. Rival IQ's own key takeaways say engagement fell 16% on Instagram, 34% on TikTok, 36% on Facebook and 48% on X in one year. Confirmed. Socialinsider shows IG 0.50% to 0.48% but its TikTok-by-followers figure moves 2.50% to 3.7% in a year (inconsistent on-page). Practical half-life: treat any benchmark as stale after about 12 months. Re-derive HypeStake's own tier medians quarterly from the creators it has scraped.
- Definitions also change under you. Meta moved IG metrics to "Views" (Reported; sources disagree on the date). Meta's Apr 2026 update made Business Discovery `view_count` combine Instagram and Facebook views for crossposted video (Confirmed, https://developers.facebook.com/blog/post/2026/04/22/instagram-api-updates-for-partnerships-metrics-collaboration-and-engagement/). YouTube's docs say `viewCount` will include views counted when playback begins (autoplay/hover) starting Aug 24, 2026 (Confirmed, https://developers.google.com/youtube/v3/docs/videos). Any views-based baseline spanning those dates is not like-for-like.
- Recommendation: do not hard-code tier "good ER" cutoffs. Score ER as a percentile against HypeStake's own same-platform, same-tier, same-format cohort, and carry the vendor numbers above only as a cold-start prior.

## 2. Fake-follower / inauthentic-engagement signals from public data

### Peer-reviewed or preprint evidence
| Study | What it shows | Status |
|---|---|---|
| Cresci et al., "Fame for sale", Decision Support Systems 2015, https://arxiv.org/html/1509.04098 | Ground truth: 3,351 bought Twitter fake followers (bought April 2013, three markets) undersampled to 1,950 vs 1,950 verified humans. Media rules performed badly. Socialbakers rule "friends:followers >= 50:1" had precision 0.997 but recall 0.162 (MCC 0.296); Stateofsearch "following:followers ~100:1" best MCC 0.205; Camisani-Calzolari 22-criteria score precision 0.974, recall 0.062, accuracy 0.548. A lightweight ML classifier on cheap features got >95% accuracy on its training set. | Confirmed (read first ~100K of 188K chars of the HTML; abstract also read) |
| Akyon and Kalfaoglu, "Instagram Fake and Automated Account Detection", arXiv 1910.03090 | Public datasets: 1,002 real + 201 fake accounts; 700 real + 700 automated. Reported accuracy 96% (fake) and 86% (automated); F1 about 94% (fake, with SMOTE-NC oversampling) and about 86% (automated, SVM/NN). Features include follower count, following count, follower-to-following ratio, private flag, post counts, bio. Authors explicitly flag unrealistic dataset bias in the follower-count features and use cost-sensitive feature selection to cope. | Confirmed (pdftotext of the PDF; abstract and tables) |
| Sayyadiharikandeh et al., CIKM 2020, https://arxiv.org/abs/2006.06867 | Supervised bot classifiers show "severe performance deterioration" on bot types absent from training data; an ensemble of per-class classifiers improved F1 on unseen accounts by 56% on average; deployed in Botometer v4 (cross-validation AUC 0.99). | Confirmed (abstract) |
| Weerasinghe et al., "The Pod People", WWW 2020 (doi 10.1145/3366423.3380256) | 1.8M Instagram posts from Telegram engagement pods; two models for pod-boosted posts with AUC 0.91 and 0.94; pod comments lean generic ("nice pic", "wow"). | Reported (Drexel/NSF record and press summaries, not the PDF) |
| arXiv 2405.10231 (influencer cartels) and 2002.07173 (impersonator comments on IG) | Collusive engagement groups and impersonator comment fraud exist; neither is covered by simple ratio rules. | Reported (abstracts via search only) |

### Which signals have measured precision
- **Follower:following ratio (high following, low followers on the *follower* accounts)**: measured, but on bought-follower Twitter data from 2013 and on small Instagram sets. High precision, very low recall for the fixed ratios (Cresci: 0.997 precision at 50:1, recall 0.162). It catches crude fakes only and is a weak sign for modern, aged or "premium" fake accounts. Also note the ratio applies to the *followers' accounts*, which public pages rarely let you enumerate at scale. On the *creator's own* ratio (e.g. follows 7,000, followed by 9,000) no study I found gives a threshold; Unverified.
- **Engagement-pod / generic comments**: measured AUC 0.91-0.94 (Reported). Needs comment text. Defensible as a risk flag, not proof.
- **Follower growth spikes**: used by vendors (HypeAuditor says it monitors "sudden, unnatural spikes in followers or engagement" and mass follow/unfollow patterns; Confirmed that the page says so, https://hypeauditor.com/how-calculate-influencer-rankings/). No public precision or threshold. Needs a time series, so only available if HypeStake snapshots follower counts itself. Spikes also come from legitimate virality or a viral post; label as "needs explanation".
- **Comment-to-like ratio, engagement vs size curve, view-to-follower ratio**: I found no peer-reviewed threshold for any of the three. The view-to-follower ">10% strong, <1% problem" cutoffs come from a single vendor guide (Reported; vendor-sourced, not a benchmark). Use them only as within-cohort percentiles (e.g. flag if the creator is below the 10th percentile of the same-platform, same-tier cohort), and report it as "unusual", not "fake".
- **Vendor ML detectors**: HypeAuditor claims 50+ behavioral patterns and 95.5% accuracy. Confirmed that they claim it; the page gives no ground truth, no metric definition, no weights. Unverified accuracy. Phyllo (a vendor blog, Reported) argues nobody outside the platforms has ground truth for who is fake, so published precision figures are not independently checkable. I agree with the logic: published accuracies come from purchased-fake or hand-labelled sets that are easier than real-world fakes.
- Regulatory frame: FTC Consumer Reviews and Testimonials Rule, 16 CFR Part 465, effective 2024-10-21, covers selling or buying fake social-media indicators (follower/view counts). The FTC Q&A says hiring an influencer who happens to have fake followers is not by itself liability. Reported (ftc.gov results via search; pages not opened).

### Recommendation for HypeStake
Emit `authenticity_risk` as a bounded risk class (low / elevated / high / insufficient-data) built from several weak, independently explainable flags, each listed to the user. Never emit "X% fake followers" from public data alone. That number is a vendor model output with no public validation. Confidence stays Low or Medium unless the creator supplies first-party audience data.

## 3. Audience-fit inference when demographics are not public

**Defensible from public data (with the caveat)**
- Content topic and format, from captions, hashtags, video text/transcripts, sponsor history. Directly observable. Confidence: High for niche fit.
- Creator-declared location and language (bio, profile fields, caption language). Observable but declares the creator, not the audience. Medium.
- Language mix of *commenters* as a coarse audience-geography proxy (for example "share of non-English comments"). Plausible, but a comment is a tiny, self-selected, bot-contaminated sample of the audience, and language is not country (English, Spanish, Arabic, Portuguese span many markets). Low to Medium; present as a proxy label, never as a percentage of audience.
- Brand/creator collaboration graph and co-mentions. Observable; Medium for adjacency.

**Not defensible from public data**
- Audience age, gender, income, country percentages. Anything shown as a precise split from a scraped or modelled source is an estimate. Profile-based demographic inference exists (Wang et al., WWW 2019, multimodal model on name, bio, photo across 32 languages, with post-stratification to correct bias; Reported from the abstract, accuracy tables not read) but it infers attributes of *accounts you can see*, such as commenters, and the bias correction depends on ground-truth population counts. It does not recover the demographics of silent followers. Text-based location inference for users is a studied problem (Zheng, Han and Sun, IEEE TKDE 2018 survey; Reported, summary only; no accuracy numbers read). The state of the art is coarse and degrades on short text.
- **TikTok audience endpoint**: I found no official public per-creator audience endpoint. TikTok's Creator Marketplace API (announced 2021) gave approved marketing partners first-party audience data (Reported, TechCrunch 2021). The third-party "TikTok audience" endpoints I found are unofficial; ScrapeCreators' page says it is unofficial, returns audience *countries* only, and does not say where the data comes from or whether it is estimated (Confirmed on that page, https://scrapecreators.com/tiktok-user-s-audience-demographics-api). Another vendor (Firebox) says its figures are estimated model outputs (Reported). Treat as Unverified third-party data: label Low confidence, show provenance, never use as a hard gate.

**Known failure modes (judgment unless noted)**
1. Commenters are not followers; heavy commenters skew toward super-fans and pods.
2. Fake or purchased followers distort any follower-based geography.
3. Language is not country; code-switching and translated comments misclassify.
4. Creator location is not audience location (expat creators, global niches, travel).
5. Hidden or zeroed counts: Instagram returns `like_count` as 0 for media where the owner hid likes when queried indirectly (Confirmed, https://developers.facebook.com/docs/graph-api/changelog/non-versioned-changes/may-26-2021). Treat 0 as "missing", not as zero engagement.
6. Age-gated or private professional accounts are not returned by Business Discovery (Confirmed, Meta Business Discovery docs).
**Upgrade path:** audience-fit confidence becomes High only when the creator connects first-party analytics (OAuth insights) or sends a media-kit audience screenshot that HypeStake stores with a "creator-supplied, unverified" tag.

## 4. Outlier and baseline methodology (median lift)

**Is median lift sound?** Yes as a within-creator normalizer, with caveats. No academic standard exists; practice is vendor-driven.
- Practice (all Reported, vendor sources): Eden flags a post as an outlier at >=2x the median of the creator's other posts of the *same type*; scores Reels on views and posts on likes, each against its own baseline (comparison set: larger of last 7 days or last 30 posts of that format). Another tool shows an outlier score only after >=10 posts. HypeAuditor's average-views calculator takes recent Reels, trims unusually high/low, and uses the median view count. Guides recommend the last 10-12 or 10-20 posts, not cherry-picked. None of these cites an experiment.
- **Sample size (Computed; assumes independent log-normal views, which real posts are not, because creators drift and formats mix):** the median of n posts vs the true median, 80% interval of the ratio:
  | n | spread sigma=0.8 | spread sigma=1.2 |
  |---|---|---|
  | 6 | 0.64-1.64 | 0.51-2.14 |
  | 10 | 0.69-1.48 | 0.58-1.83 |
  | 12 | 0.71-1.43 | 0.60-1.71 |
  | 20 | 0.76-1.32 | 0.66-1.52 |
  | 30 | 0.80-1.26 | 0.71-1.41 |
  So with n=10 the baseline itself can be off by about 1.5-1.8x either way. A "2x median" outlier rule on 10 posts is therefore weak evidence; require n>=12 for a Medium-confidence baseline, >=20-30 for High, and report the interval or an `n` badge.
- **Age-of-post bias (Confirmed, academic):** Italian-influencer dataset of 651 influencers, about 4M posts, 13B interactions on Facebook and Instagram, 2016-2021 (ASONAM 2021, "Temporal dynamics of posts and user engagement of influencers on Facebook and Instagram", https://iris.unito.it/bitstream/2318/1843099/1/ASONAM21_Post_Interaction_Evolution.pdf): on average 50% of interactions arrive within 4 hours on FB and 2 hours on IG; most posts live 20-50 hours; early interactions (first hour or even first 15 minutes) predict later popularity. So likes and comments on IG/FB posts older than about 2-3 days are near final. Blog claims for TikTok (under 1 hour half-life) and YouTube (weeks to years) are Reported with inconsistent numbers (Scott Graffius, GenSumo, Neil Patel). Rule I would use (judgment): exclude posts younger than 72 hours from IG/TikTok baselines and younger than 14 days from YouTube baselines; flag, don't blend.
- **Format handling (judgment):** separate baselines per platform x format (Reel, carousel, image, Story-not-public, Short, long-form video, livestream). Do not pool formats; Rival IQ and Socialinsider both show carousel/image/Reel ER differ (Confirmed). Use `view_count` where available, `like_count` only when it is not zero-masked.
- **Robustness (judgment):** report median, MAD (or IQR) and the lift of the latest N; exclude pinned posts and ones with a paid-partnership flag from the *organic* baseline, and compute a separate sponsored-vs-organic ratio when >=5 sponsored posts exist. Optionally log-transform views before computing spread.

## 5. Brand-safety screening from public data

**Status of GARM (Confirmed):** WFA statement dated 9 Aug 2024: GARM "will discontinue its activities"; the WFA GARM page says "GARM was discontinued on August 8 2024." The statement names the Brand Safety Floor and the Adjacency Standards Framework as GARM tools and names no successor or new owner. Sources: https://wfanet.org/knowledge/item/2024/08/09/wfa-discontinues-garm, https://www.wfanet.org/garm. The framework document itself is members-only, so I could not verify the category list from a primary source (the IAS page I opened was gated).
**What replaced it:** I found no single successor. Reported (Digiday, AdExchanger, Forrester, VideoWeek summaries): platform and vendor policies built on the GARM taxonomy remain in use; DoubleVerify, IAS and Zefr still sell GARM-style tiers; responsibility moved to each advertiser, and Forrester notes antitrust caution about advertisers coordinating on content standards. The 4A's Advertiser Protection Bureau published the original floor and suitability framework in 2018 (Reported: ppc.land; I could not read the 4A's page). I found no IAB Tech Lab replacement standard. Net: use the GARM-style taxonomy as a de facto vocabulary and make the *brand's own* thresholds explicit and configurable.
**Category scaffold (Unverified, from memory of the GARM taxonomy; verify before shipping):** adult and explicit sexual content; arms and ammunition; crime and harmful acts, human-rights violations; death, injury or military conflict; online piracy; hate speech and acts of aggression; obscenity and profanity; illegal drugs, tobacco, vaping, alcohol; spam or harmful content; terrorism; debated sensitive social issues; plus misinformation (added later, Unverified). Risk tiers: floor, high, medium, low.

**Practical scan checklist (design judgment)**
1. Last 20-30 posts (or 90 days, whichever is more) per platform: caption, on-screen text/transcript, hashtags, thumbnails/frames. Classify each against the category scaffold with a per-category risk tier; record the post URL as evidence for every hit.
2. Comments on the last 10 posts: slurs, harassment, spam/scam links, pod-style generic comments (feeds both brand safety and authenticity).
3. Controversy: news and search hits for the creator name plus "lawsuit", "scam", "apology", "cancelled"; past brand-partner removals if public.
4. Sponsor-disclosure compliance on sponsored-looking posts: see section 6. FTC "Disclosures 101" (Confirmed, https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers): disclosure must be hard to miss and with the endorsement; "ad", "advertisement", "sponsored" are generally enough; vague terms like "sp", "collab", "thanks" are not; do not assume a platform tool is good enough; in video the disclosure should be in the video, not only the description; disclosures hidden behind "MORE" are likely missed; #ad is optional ("fine but not necessary").
5. Competitor and category conflicts: recent paid promotion for direct competitors; exclusivity risk.
6. Account integrity: handle changes, deleted-post history is not public (Unverified), bio claims vs evidence.
Output: per category `none / low / medium / high / floor`, with evidence links, an `n_posts_scanned` and a confidence label (LLM classification of text is Medium; of images/video frames is Low to Medium and should carry a human-review flag).

## 6. "Does this creator distribute for others?" (seller-vs-buyer / sponsor-readiness)

**Platform flags and what is exposed publicly**
| Platform | Flag | Publicly readable? | Status |
|---|---|---|---|
| YouTube | `videos.list` accepts `part=paidProductPlacementDetails`; object field `hasPaidProductPlacement` (boolean, default false). Also a `brandPartner` part is listed. Creator-set via "Yes, my video includes branded content" and shows a label at the start of the video. | The `part` is listed and only `fileDetails`, `processingDetails`, `suggestions` are stated as owner-only. The docs do not say whether an API key suffices; I did not make a live call. Quota 1 unit/call; default 10,000 units/day. | Confirmed (docs: https://developers.google.com/youtube/v3/docs/videos/list, https://support.google.com/youtube/answer/154235, https://developers.google.com/youtube/v3/getting-started). Public readability via API key: Unverified, test it. |
| Instagram | "Paid partnership" label (optionally "with [Brand]"). Content Publishing API can now *set* it (Apr 2026). | Business Discovery docs list `followers_count`, `media_count`, and per-media `comments_count`, `like_count`, `view_count`; no partnership field is mentioned there or in Meta's Apr 2026 post. Only professional accounts are returned. | Confirmed that no read-side field is documented in the two pages. Whether the label is scrapeable from the public web view: Unverified. |
| TikTok | "Commercial Content API" `POST /v2/research/adlib/commercial_content/query/`: fields `id, create_timestamp, create_date, label` (e.g. "Paid partnership"), `brand_names`, `creator`, `videos`. Scope `research.adlib.basic`. | Country filter supports EEA countries only (UK and Switzerland excluded); data after 2022-10-01. Page does not state who is eligible; a vendor blog says research-institution access only (Reported). | Confirmed (https://developers.tiktok.com/doc/commercial-content-api-query-commercial-content). Eligibility for HypeStake: Unverified, likely not available. |

**Caveats (judgment unless noted)**
- These flags are creator-set, so absence is not evidence of no sponsorship. Undisclosed sponsorship is exactly what the FTC guide warns about. A creator with many clearly sponsored posts but zero flags is a compliance risk, not a clean record.
- The caption-based fallback is #ad, #sponsored, "paid partnership", "in partnership with", affiliate links/discount codes, and brand @-tags. A single vendor reported a Sway Ops figure that over 50% of engagements on one day's #ad/#sponsored Instagram posts were fake (Reported via Digiday, vendor data, one day); treat as a reason to cross-check, not a rate.
- Media kit, "business inquiries" email, rate card link, link-in-bio storefront, and talent-manager listing are plausible *sponsor-readiness* and *contactability* signals but I found no published evidence on how well any of them predict willingness or ability to deliver a sponsorship; Unverified. Score them as sponsor-readiness evidence (observable, low-weight), not as quality evidence.
- Sponsor-saturation: share of last 20 posts with a paid flag or ad-like caption. High saturation may lower audience trust; I found no study; Unverified. Use as a flag, not a penalty, until calibrated.

## 7. Recommended scoring design (0-100). All weights are judgment, not research results.

### Structure
1. **Eligibility gates (binary, evaluated first).** A gate failure means "do not recommend / manual review", independent of any weighted score. Show the reason and the evidence link.
   - G1 Brand-safety floor hit in the last 12 months (high-severity category with evidence).
   - G2 Strong inauthenticity evidence: documented purchased followers/views, an engagement-pod pattern across several posts, or a platform/regulator action. A single ratio flag never triggers a gate (see section 2).
   - G3 Insufficient observable data: fewer than 10 public posts in 90 days on the scored platform, or a private/age-gated account. Output "insufficient data", not a low score.
   - G4 Identity unverifiable: cannot match the profile to a stable real identity or name (impersonation risk).
   - G5 Persistent undisclosed-sponsorship pattern (sponsored-looking posts repeatedly lacking disclosure), marked "compliance risk". Consider making this a review gate rather than a reject, since it is a judgment call.
   - Optional brand-specific gates: competitor exclusivity, country/market mismatch, category exclusions (configurable per brand).
2. **Weighted dimensions** (sum 100; each sub-score 0-100, then multiplied by weight):
   | Dimension | Weight | Main inputs | Typical confidence |
   |---|---|---|---|
   | Niche fit | 20 | topics, hashtags, transcript embedding similarity to brief | High |
   | Audience fit | 15 | commenter language/geo proxy, topic overlap, creator-declared location; creator-supplied analytics if present | Low-Medium (High only with first-party data) |
   | Reach | 10 | followers and median views on the right format, as cohort percentile | High (counts public) |
   | Engagement quality | 15 | median ER vs cohort percentile, median lift stability, comment substance | Medium |
   | Authenticity (inverse of risk) | 15 | pod/generic-comment flags, growth spikes (if snapshotted), ratio anomalies, ER-vs-size outliers | Low-Medium |
   | Brand safety (beyond gate) | 10 | tiered category results below floor, controversy | Medium |
   | Sponsor-readiness | 10 | disclosure habits, paid-flag history, delivery consistency (posting cadence), media kit | Medium |
   | Contactability | 5 | public email/contact route, manager/agency listing, response channel | High (observable) |
   Why these weights: fit and quality dominate because a clean but misfit creator is useless, so niche + audience + engagement = 50. Authenticity gets 15 because it is the largest loss driver but is also the least measurable from public data, so it should move the score but should not dominate. Reach is 10 because, once real, it is price-driven and scales cost. Contactability is 5 because it is a practical, not quality, factor. All of this is judgment.
3. **Confidence and missing data.** Each dimension returns `score`, `confidence` (High / Medium / Low / None) and `evidence_count`. If a dimension has confidence None, drop its weight and renormalize over the rest, then cap the overall confidence at Low and show "not scored: X". Never impute zero. Report the final as a band, e.g. "72 (range 62-80, overall confidence Medium)", where the band is the score recomputed with each Low-confidence dimension set to its pessimistic and optimistic bound. Show a short "what would raise confidence" line (e.g. "connect Instagram insights", "provide 3 more months of snapshots").
4. **Penalty rule for dimension floors (design option).** If authenticity < 40 or brand safety < 50, cap the total at 60 and tag "needs human review". This keeps the rubric transparent without hiding a bad component inside an average.
5. **Transparency requirements.** Every score ships with: version of the rubric, each dimension's inputs, `er_basis`/`n_posts`/`post_age_cutoff`, data-collection timestamp, cohort used for percentiles, and the list of flags with links.

### What data would let HypeStake calibrate (replace the judgment weights)
- Outcomes per deal: creator replied, accepted, signed, posted on time, disclosure compliant, brand-rated fit, delivered views/clicks vs the price paid, repeat engagement, any dispute. These are the labels.
- Pre-deal snapshots of the same public features (so the model sees what the vetter saw), with deal terms and dates. Without time-stamped pre-deal features you cannot avoid leakage.
- Brand-reported fraud or "non-performing" outcomes, to estimate precision of each authenticity flag; this is the ground truth the literature lacks.
- First-party analytics where creators connect them (audience geography, true reach), to measure the error of the public proxies in section 3.
- Method once enough deals exist: start with a regularized logistic (or ordered) model on the dimension sub-scores to predict "good outcome"; compare its coefficients to the judgment weights; use isotonic/Platt calibration so "72" maps to an observed success rate; evaluate per platform and tier. Keep gates rule-based so a model can never override a safety floor.

## 8. Gaps and what I could not verify
- Rival IQ, Socialinsider and Favikon are vendor datasets of brand/business accounts, not random creators. None gives a clean creator ER-by-tier table with median; the best verified creator-adjacent number is Rival IQ "Influencers" (0.576% IG, 1.11% TikTok, by followers, median, CY2024).
- Socialinsider's three benchmark pages contain internal inconsistencies (2024-2026 labels, differing averages). I report the table values and flag the inconsistency.
- No peer-reviewed threshold exists for comment-to-like ratio, ER-vs-size curve, or view-to-follower ratio. No measured precision for growth-spike detection.
- GARM category list is from memory, because WFA and IAS pages are members-only or gated. The 4A's page did not load usefully; the 2018 date is Reported.
- Did not make live API calls (YouTube `paidProductPlacementDetails` with an API key; Instagram Business Discovery on a real account). Both are cheap tests to run before committing the design.
- Emplifi, HypeAuditor 2025/2026 and Influencer Marketing Hub reports were not read in full (gated or 404); anything attributed to them is Reported.
