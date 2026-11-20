# Content site or product site

Use this after contact capture has reached a creator's own site and before the row moves on. The question: does this person publish for an audience a brand could pay to reach, or do they run a product and want traffic for it? A shortlist wants the first kind. Address rules are in `contact-capture-rules.md`. Status names are defined in `../skills/creator-research/SKILL.md`.

The signal directions below are working heuristics written on 2026-11-02, not measured results. Label a small sample of HypeStake creator sites by hand, compare the tally with your labels, and put the sample size in the run report before trusting it.

## Decision flow

1. **Is this the creator's own site?** If the link is a tipping, payment, course, booking or shortener page, or a platform subdomain, stop. A sponsorship page on someone else's platform says nothing about this creator.
2. **Tally structural signals on the homepage already fetched** (table below). Keyword hits are noted, never tallied.
3. **Read the tally.**

| Tally | Decision | Status | Stored |
|---|---|---|---|
| Content signals only | Content site | unchanged, row continues | contacts, plus the deciding signals in `signals` |
| Product signals only | Product site | `buyer` | verdict in `reason`, signals, domain and handle. Nothing goes in `contacts[]` |
| Nothing structural either way | Unresolved | `held` | `reason` names the page still missing |
| Both kinds | Mixed | `held` with reason "content and product signals" | both signal sets. A person may admit a creator who also sells a product |

4. **Fine pass, only when step 3 gave `held` or a keyword flag is open.** Read the pages in fetch scope you have not read yet (the contact or about page, and the sponsor page), re-tally with them, and decide again. No fetch happens beyond those pages. If both were already read, leave the row `held`.

No outcome here sets `qualified`. The final stage of the run sets it, and only if every earlier stage passed.

## Signals

| Signal | Type | Points to |
|---|---|---|
| Feed link (RSS or Atom) in the page head | structural | content |
| Hosted on a newsletter, blog or podcast platform | structural | content |
| Sponsor, advertise or media-kit page, or ad slots on the homepage | structural | content |
| Checkout or payment script for a product | structural | product |
| Per-seat or plan pricing table with monthly prices | structural | product |
| Sign-in or app link in the main navigation | structural | product |
| subscribe, archive, newsletter, blog, pricing, sign up, demo, sponsor, partner | keyword | flag only |

Why keywords never count: most software products keep a blog, creators who sell courses keep a pricing page, and sponsorship wording in running text is often about somebody else's sponsor. Why one structural signal cannot beat another by itself: a paid newsletter shows prices and may embed a checkout, so a price or checkout alone does not outweigh a feed.

A deal inbox such as partnerships@ nominates a candidate. On a product site it usually means "partner with us", so it decides nothing by itself.

Platform behaviour from discovery data is free supporting context. Repeated original posts on varied topics fit a creator. Repeated promotion of one product fits a founder. A single post that took off is usually a launch.

## Why log a buyer

A product founder is the wrong target for promoting other brands. Logging the site as `buyer` stops later rounds from fetching it again and keeps the evidence if HypeStake ever wants brand-side leads. That would be a separate product decision, and any use of the address goes through `../skills/outreach-compliance/SKILL.md`.

## Limits

- Platforms differ in how many founders versus creators they surface. Measure the mix per platform from your own sample and do not carry one platform's mix to another.
- A flagged or tied site costs one more fetch, so a wrong flag is cheap. A wrong `buyer` on a real creator costs more, which is why `buyer` needs structural evidence and a keyword flag is never enough.
