---
name: creator-vetting
description: Vet creators or influencers from public data and return gates, a confidence-labelled 0-100 score with a band, and the evidence behind each dimension. Covers niche and audience fit, engagement quality against a median baseline, authenticity risk, brand safety, FTC disclosure habits, sponsor readiness and whether a captured contact exists, scored by ../../scripts/creator_score.py. Use for "vet these creators", "is this influencer legit", "check for fake followers", "audience fit for our market", "brand safety check", "score and rank my shortlist", "creator teardown", "due diligence before a deal". Does not find creators (creator-discovery), capture emails (creator-contact-capture), clear outreach (outreach-compliance) or look up one endpoint (scrapecreators-api).
allowed-tools: Read, Write, Bash, WebFetch
license: MIT
---

# Creator vetting

## Overview

This skill answers one question for a shortlist: is this creator a safe, credible and relevant partner for this brand, and how sure are we? It runs five gates (G1 to G5), scores eight weighted dimensions on a 0 to 100 scale and reports the score with a band and a confidence label. The arithmetic lives in `../../scripts/creator_score.py` (tested, stdlib only). The agent supplies dimension scores and gate codes, and the module returns the verdict. Do not reimplement or edit it.

It reuses `outlier-post-finder` for the baseline procedure and the authenticity mode of `comment-mining` for comment counts and the commenter language label, so neither procedure is repeated here. It owns `/v1/find-social-profiles` (identity matching for G4). Contact capture owns `/v1/find-creator-emails`.

Detail, thresholds and evidence rules are in `../../references/scoring-rubric.md` (the rubric). Read the section named in each step before scoring that part. The weights, thresholds and cutoffs are judgment defaults, not research results. The score is a transparent summary, not a prediction, until it is calibrated against deal outcomes (rubric section 9).

Hard limits from public data: never output a "% fake" figure, never output exact audience age, gender or country percentages, and treat an Instagram `like_count` of 0 as missing. Prices, quotas and paths in this file: Last verified 2026-11-02.

## When to Use

- A shortlist needs ranking, or one creator needs a go or no-go before outreach or a deal.
- The user asks about fake followers, authenticity, audience fit, brand safety, disclosure habits or "is this creator legit".
- The user wants a creator teardown (positioning, content pillars, outliers) for a partnership decision.

| Request | Use instead |
|---|---|
| Find creators in a niche | `creator-discovery` |
| Get a creator's business email or contact page | `creator-contact-capture` |
| May we email or store this list | `outreach-compliance` |
| Which endpoint returns a field | `scrapecreators-api` |
| Why did one post beat the baseline, for content ideas | `outlier-post-finder` |
| What are people saying in the comments, for product or copy | `comment-mining` |

## Workflow

1. **Check the route, then fix the brief.** Read the source policy table in `../outreach-compliance/SKILL.md` for every source this run will use: post and comment pulls, `/v1/find-social-profiles`, any audience lookup. A source marked `prohibited` or `review_required` (ScrapeCreators is `review_required`) is skipped with a note in the run report, unless the user's current request names that source and the vendor or API explicitly. If no allowed route can supply the posts, stop and set `status: held` with `reason: "route blocked by the source policy table"`. Do not raise G3 for this, because G3 means the public data is thin, not that fetching was not permitted. Then record the brief: target market and language, platforms and the deal format (for example Reels or long video), product category, exclusions, and the brand's safety configuration (floor categories, tolerated tiers, excluded competitors). If the user gave no safety configuration, say so and use no tolerance for any category, then mark brand safety low confidence. Ask only when a missing fact would change the result. Check the credit balance with `GET /v1/account/credit-balance` before paid pulls.

2. **Check data sufficiency and identity first.** They cost little and decide G3 and G4. Count public posts in the last 90 days on each scored platform (under 10, or private or age-gated, means G3). Match the profile to a creator-owned site or link-in-bio and to same-handle accounts elsewhere with `/v1/find-social-profiles` (`platform` and `handle`, 10 credits per live lookup, 0 on a cache hit, Last verified 2026-11-02). It returns a confidence-scored identity graph, so record the confidence it gives next to each match. HypeStake writes a discovered URL to a Creator record only at confidence 0.8 or higher, and an empty `profiles` list means the source handle did not validate, not that nothing is linked (checked against HypeStake source 77a68e5c, 2026-11-10). It accepts a YouTube `@handle` or 24-character channel id, not a `/c/` or `/user/` name. Disagreement without explanation means G4. Stop and report if either gate fires.

3. **Pull posts and build baselines.** Follow `outlier-post-finder` steps 2 to 5 for feeds, metric normalisation and median baselines, one platform and one format at a time. Vetting differences:
   - Pull at least 20 posts, 12 as a floor. Use the module's confidence cutoffs (12 medium, 20 high), which are stricter than that skill's 10.
   - Always include `age_hours` on each post. The module drops posts younger than 72 hours and leaves out, and counts, posts with no age or no metric value (`excluded_unknown_age`, `excluded_missing_metric`). For YouTube pass `"min_age_hours": 336` in the input.
   - Set a hidden or zero Instagram `like_count` to null.
   - Remove pinned and paid-partnership posts from the organic baseline.
   - From this skill's folder, run `python3 -I -B ../../scripts/creator_score.py < posts.json`, with `{"metric": "views", "posts": [...]}` as input. Keep `er_basis`, `stat` and `n_posts` with every ER value (rubric section 4).

4. **Teardown pass.** From the posts and profile, write down positioning (who they serve, promise, voice), three to five content pillars with example URLs, recurring formats and series, and the top outliers from step 3 with lift. This feeds niche fit and sponsor readiness. Quote only visible captions or fetched transcripts. Do not copy private details.

5. **Comment pass.** Run `comment-mining` in its authenticity mode on the last 10 posts (at least 100 comments across 5 posts to judge anything). It returns per-post counts of generic or pod-style, spam or scam and substantive comments, a commenter language label and the substantive share. Use the counts for flags F1 and F2, the share for the engagement bonus and the label for the audience-fit check. Treat bot and spam comments as an authenticity signal, not as audience voice.

6. **Audience-fit checks and country.** Rate creator-declared location and language, commenter language label and topic overlap against the brief (rubric 3.2). Set `country` on the record to the country the creator declared (bio or profile field), or null if none. Never infer it from comment language or an audience list, because a null country blocks sending in `outreach-compliance` and a wrong one clears it by mistake. Optionally call `/v1/tiktok/user/audience` for a shortlisted TikTok creator: 26 credits, `handle` only, country list only, no age or gender, no `cache_max_age` (Last verified 2026-11-02). Confirm the spend with the user, keep it supporting evidence only, and label it unverified third-party data. Flag any gap between creator location and audience location.

7. **Brand-safety and disclosure scan.** Follow rubric sections 7 and 8: last 20 to 30 posts per platform, comments on 10, controversy search, competitor conflicts, disclosure on sponsored-looking posts. GARM was wound down by the WFA (announced 9 August 2024, no successor named), so use the category list as vocabulary only and apply the brand's own thresholds. Record a URL for every hit.

8. **Evaluate gates G1 to G5** with rubric section 2. Pass the codes to the module. Any gate returns `reject` with `score: null`. Report the gate and its evidence link, and for G3 say "insufficient data". Set `status` to `gated:G#` using the lowest code that fired, and list every code in `gates`. Brand-specific exclusions are not gates: drop the creator from the shortlist, set `status: held` with the exclusion as `reason`, and do not invent a gate code.

9. **Score the eight dimensions** with rubric section 3. For each give a score or `null`, a confidence of low, medium or high, and a one-line evidence string. Use `null` when public data cannot support a score, never 0 or 50. Count each piece of evidence in one dimension only. Read `contact_tier` from the record for contactability (rubric 3.8): `email`, `business_inbox` or `form` scores 100, `manager_listing` 70, `dm_only` 40, `none` 0, and a missing tier (contact capture did not run) is `null`.

   | Dimension | Weight | Confidence ceiling from public data |
   |---|---:|---|
   | niche_fit | 20 | high |
   | audience_fit | 15 | medium (high needs creator-connected analytics) |
   | engagement_quality | 15 | medium |
   | authenticity | 15 | medium |
   | reach | 10 | high |
   | brand_safety | 10 | medium (high after human review) |
   | sponsor_readiness | 10 | medium |
   | contactability | 5 | high |

10. **Run the module.** Build `vet.json` as `{"dimensions": {name: {"score": n, "confidence": c, "evidence": "..."}}, "gates": []}` and run `python3 -I -B ../../scripts/creator_score.py < vet.json` from this skill's folder. Read the result literally:
    - Missing dimensions are dropped and the rest are renormalised. Overall confidence becomes low whenever any dimension is missing, and it is otherwise the weakest present dimension.
    - Authenticity below 40 or brand safety below 50 caps the total at 60. Report `floor_capped_by`.
    - The band is a fixed width by confidence (plus or minus 5, 10 or 20), not a statistical interval.

11. **Set the status.** A gate or a brand exclusion sets it as above. Otherwise the record stays `candidate`, unless vetting is the last stage the run included: then set `qualified` only if the record arrived as `candidate` and the score and contact meet the run's definition of qualified (`../creator-research/SKILL.md`).

12. **Write the report** in the Output Format below. When ranking a shortlist, sort by score but treat creators whose bands overlap as tied, and list gated creators separately with their reasons. Save the transparency record (rubric section 10) beside the report.

## Output Format

```markdown
# Creator Vetting: {creator} ({platform}, {format})

## Verdict
- Result: score {n} (band {lo} to {hi}) | reject: {gate codes and reasons}
- Status: candidate | qualified | gated:G# | held ({reason})
- Overall confidence: low | medium | high ({why: weakest dimension or missing list})
- Floor cap applied: {none | dimension}
- Not scored: {dimension: reason}

## Gates
| Gate | Status | Evidence link |
|---|---|---|

## Dimensions
| Dimension | Score | Confidence | Evidence (counts, window, cohort) |
|---|---:|---|---|

## Teardown
- Positioning:
- Content pillars (with example URLs):
- Top outliers (lift, URL):

## Audience notes
- Geography and language (labels, never percentages):
- Comment quality and substantive share:
- Provenance of any third-party audience data:

## Risk signals
- Authenticity flags F1 to F4 (each with link, worded as "risk signal, not proof"):
- Brand-safety hits by category and tier:
- Disclosure check on sponsored-looking posts:

## Next research step
- Continue to outreach checks | Continue after named checks | Stop, and why in one sentence
- What would raise confidence:
- This is a research next step, not advice to accept a deal, set terms or invest.

## Record
- rubric_version, collected_at, er_basis, stat, n_posts, post-age cutoff, cohort, brand config, overrides, contact_tier, country
```

## Common Pitfalls

- Reporting a vendor or self-made "X% fake followers" or exact audience demographics. Public data cannot support either, so report flags and labels.
- Treating one flag (a ratio, a spike) as proof or as a gate. G2 needs documented purchases, a pod pattern on at least 5 of 10 posts, or a regulator or platform action.
- Zero-filling a dimension you could not measure. Set it to `null` so the module renormalises and lowers confidence.
- Reading Instagram `like_count` 0 as zero engagement. Hidden likes return 0 or omit the field, so set it to null.
- Posts without `age_hours`. The module leaves them out and counts them, so a feed with no ages yields no baseline. Supply the age.
- Pooling platforms or formats into one baseline, or mixing ER bases and statistics (followers versus views, mean versus median) with a benchmark.
- Using a vendor benchmark as a target. Rival IQ and similar figures are brand-account samples that fall year over year, so cite them as dated priors only (rubric section 5).
- Comparing views across metric-definition changes (Meta crossposted video from April 2026, YouTube from 2026-08-24).
- Reading a missing platform sponsorship flag as "not sponsored". Flags are creator-set.
- Treating the TikTok audience country list as fact, or buying it for the whole list at 26 credits each. Use it only on a shortlist.
- Applying GARM tiers as if the standard were current, or applying thresholds the brand did not set.
- Reading the band as a statistical interval, or ranking creators whose bands overlap as if the order were certain.
- Using the score as a prediction. It stays a judgment-default summary until calibrated with deal outcomes.
- Calling it a Match Score. It is not pairwise and not HypeStake's matching engine output. Show it as a creator score with its band, confidence and gates.
- Sending outreach or storing contact data from this skill. Contact capture and sending belong to `creator-contact-capture` and `outreach-compliance`.
