---
name: comment-mining
description: Use when the user wants to mine comments and replies for audience reactions, customer language, questions, objections, complaints, product ideas, buying intent, sentiment, or voice-of-customer insights from public social posts and videos. Also has an authenticity mode for creator-vetting that counts generic, pod-style and spam comments before filtering and returns a commenter language label and the substantive share.
allowed-tools: Bash, Read, Write, WebFetch

version: 1.0.0
author: ScrapeCreators
license: MIT
homepage: https://scrapecreators.com
repository: https://github.com/ScrapeCreators/social-media-research-skills
metadata:
  openclaw:
    requires:
      env:
        - SCRAPECREATORS_API_KEY
    primaryEnv: SCRAPECREATORS_API_KEY
    homepage: https://scrapecreators.com
    tags:
      - social-media
      - research
      - scrapecreators
---

# Comment Mining

## Overview

Mine public comments for what people ask, complain about, want, misunderstand, or repeat. The output should help with product research, content ideas, copywriting, objection handling, and audience understanding.

## When to Use

Use this skill when the user asks to:

- analyze comments on a TikTok, YouTube video, Instagram Reel, Facebook post, Reddit post, or Rumble video
- find audience questions, objections, complaints, or buying intent
- extract voice-of-customer language
- find content ideas from comments
- understand sentiment around a post, creator, product, or topic
- count generic, pod-style and spam comments on a creator's posts as an authenticity signal (authenticity mode, below), which `creator-vetting` calls by that name

## Comment Sources

| Platform | Endpoint |
|---|---|
| TikTok comments | `/v1/tiktok/video/comments` |
| TikTok replies | `/v1/tiktok/video/comment/replies` |
| YouTube comments | `/v1/youtube/video/comments` |
| YouTube replies | `/v1/youtube/video/comment/replies` |
| Instagram comments | `/v2/instagram/post/comments` |
| Facebook comments | `/v1/facebook/post/comments` |
| Facebook replies | `/v1/facebook/post/comment/replies` |
| Reddit comments | `/v1/reddit/post/comments` |
| Rumble comments | `/v1/rumble/video/comments` |

## Workflow

1. **Fetch comments**
   - Use the post/video URL whenever possible.
   - Paginate when the endpoint supports it and the user wants depth.
   - Preserve comment text, author if public, like/upvote count, timestamp, and source URL.

2. **Clean lightly**
   - Remove obvious spam/duplicates. In authenticity mode, count them first (see the section below).
   - Keep slang, misspellings, and emotional wording if it is useful customer language.
   - Do not over-normalize exact quotes.

3. **Classify each useful comment**
   Use these buckets:
   - questions
   - objections
   - complaints/pain points
   - praise
   - confusion
   - requests/feature ideas
   - buying intent
   - controversy/debate
   - jokes/memes/culture signals

4. **Cluster themes**
   - Group similar comments.
   - Score themes by frequency and intensity.
   - Highlight exact quotes for each theme.

5. **Turn insights into actions**
   Depending on the user's goal, produce:
   - content ideas
   - FAQ ideas
   - landing page copy angles
   - product ideas
   - objection-handling bullets
   - sales/support notes

## Authenticity mode

Use this mode when `creator-vetting` asks for it. Normal mode drops spam and generic comments before analysis. This mode counts them first, because they are the evidence. The calling stage has already done the route check, because comment pulls go through a metered vendor.

1. Fetch comments on the creator's last 10 posts, one platform at a time. Judge nothing below 100 comments across at least 5 posts, and say "insufficient sample" instead.
2. Before any filtering, tag every comment as one of:
   - **generic or pod-style**: praise with no reference to the content ("nice pic", "wow", emoji only), or the same short phrase repeated across posts or accounts.
   - **spam or scam**: links, "DM me to earn", giveaway or follow-for-follow text, impersonation, repeated identical text from different accounts.
   - **substantive**: asks a question, names a specific detail of the post, states an objection or shows buying intent.
   - **other**: everything else.
3. Count per post: total, generic or pod-style, spam or scam, substantive. Then list the posts where generic or spam comments are the largest group, with two quoted examples each. A reviewer decides what counts as dominant, so keep the quotes.
4. Give a **commenter language label** for the creator: the main language or languages among comments in words ("mostly English, some Spanish"), never a percentage of the audience. Emoji-only comments carry no language.
5. Give the **substantive share**: substantive comments divided by comments that are not spam or scam. Report the counts next to it.
6. Return the counts, the post list, the language label and the substantive share. `creator-vetting` turns them into flags F1 and F2, the engagement bonus and the audience-fit language check (see `../../references/scoring-rubric.md`, sections 3.2 to 3.4).

Report these as risk signals, never as proof, and never as a "percent fake" figure. Comments are a small, self-selected sample, so label the sample size and confidence.

## Output Format

```markdown
# Comment Mining Report

## Summary
- Source(s): {urls}
- Comments analyzed: {count}
- Confidence: High/Medium/Low

## Top Themes
| Theme | Type | Frequency | Intensity | Representative quote |
|---|---|---:|---|---|

## Audience Questions
- "..."

## Objections and Concerns
- **Objection:** ...
  - Evidence: "..."
  - Response angle: ...

## Buying Intent / Demand Signals
- "..."

## Exact Language to Reuse
- "..."
- "..."

## Content Ideas From Comments
1. ...
2. ...
```

## Quality Guardrails

- Label sample size and confidence.
- Separate one loud comment from a repeated pattern.
- Preserve exact quotes for useful language.
- Avoid claiming broad market sentiment from one post's comments.
- Call out moderation/platform bias when relevant.

## Common Pitfalls

- Do not flatten comments into generic sentiment. The value is in questions, objections, and exact wording.
- Do not include personally identifying details unless they are already public and necessary.
- Do not treat bot/spam comments as audience signal. In authenticity mode they are counted as an authenticity signal instead.
- Do not skip Reddit post context. For Reddit, read both the original post and comments.
