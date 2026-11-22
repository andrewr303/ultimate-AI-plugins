# Platform rules

**Checked: 2026-11-04.** Each rule cites claim IDs in `../research/2026-11-04/artifacts/claim_ledger.jsonl`, where the source URLs live. Platforms change these rules often. If a rule decides an action and this file is more than 60 days old, re-read the cited official page before relying on it, and tell the freelancer the date you checked. Items marked **unverified** could not be read from an official source; never quote them as fact to a client.

## Global rules for this plugin

- The plugin never logs in, scrapes, polls, auto-refreshes, auto-applies, or automates a browser on any marketplace. Every platform below either forbids automated access in its terms or could not be confirmed to allow it. (clm_up_001, clm_up_002, clm_pl_006, clm_pl_011, clm_pl_013, clm_pl_015, clm_pl_017, clm_pl_018, clm_pl_020, clm_pl_022)
- Default intake everywhere: alert emails the platform sends the freelancer, and listings he pastes or screenshots. Machine-read channels are limited to the rows below that name an official API, MCP, or feed.
- the freelancer submits, sends, accepts, funds, and pays. Drafts only.

## Upwork

### Automation and official access

| Rule | Claims |
| --- | --- |
| A bot or scraper is any script, program, extension, or service that automatically sends requests, collects data, or acts faster or more often than a human. Marketing as "built for Upwork" does not make a tool approved; violations bring a temporary restriction or a permanent block. | clm_up_001 |
| Named risky tools: job alert or watcher tools that scrape or run searches, auto-refresh tools, page monitors, macro and RPA recorders, user-script managers, auto-paging helpers, multi-site research tools, and anything that sends requests while the tab is idle. | clm_up_002 |
| An API key does not permit scraping or proposal spam; using browser OAuth tokens or session cookies in a script, calling website pages instead of endpoints, or background polling can flag the account. | clm_up_003 |
| API keys are for personal or internal use and need identity verification, at least $25,000 lifetime earnings or spend, a JSS of 90%+ for freelancers, and good standing. the freelancer does not currently qualify, so do not suggest one. | clm_up_004 |
| **Official Upwork MCP server** (launched 2026-08-10, no extra cost). An agent may draft a proposal through it, but the user reviews and explicitly confirms each submission. Project Catalog cannot be created or edited through MCP. | clm_up_005 |
| MCP rate limits per account: search and discovery 15/min, 150/hour, 750/day; profile viewing 5/75/250; other reads 20/250/750; job posts, proposals, offers, invitations 20/60/150; other changes 4/15/40. Daily reset 00:00 UTC; Upwork can change them. | clm_up_006 |
| **Claude connector for Upwork:** Claude prepares proposals, messages, and milestones as drafts the user approves. Accepting offers, funding or approving milestones, and changing weekly limits happen on upwork.com. | clm_up_007 |
| Upwork RSS job feeds were discontinued after 2024-08-20. Refuse "RSS replacement" tools that poll Upwork. | clm_up_031 |
| Official job-alert paths: Freelancer Plus instant job alerts (app or email, filters for hourly or fixed and minimum rate), saved searches, notification settings, Job Digest emails for Rising Talent and Top Rated, and Recommended Jobs. | clm_up_031 |

**Official Upwork agent plugin.** Upwork publishes `upwork/upwork-agent-plugin` (Apache-2.0) whose MCP config points to its first-party server at `https://mcp.upwork.com/mcp`, installable in Claude Code with `/plugin marketplace add upwork/upwork-agent-plugin` and authorized through a browser OAuth flow. It is the only live Upwork connection freelance-legend recommends; community GraphQL MCP servers need an Upwork-approved API key for that exact use and are not recommended. (clm_gh_001, clm_gh_023)

**How freelance-legend uses the official MCP or connector (only if the freelancer has connected it):** on-demand searches or reads that the freelancer asks for in the moment, counted against the limits above and stopped on any rate-limit error without retrying; drafts he then reviews. Never scheduled or continuous monitoring of the job corpus (the freelancer's own earlier reading of the API and MCP Terms, section 4.1, excludes "activity designed to enumerate or continuously monitor Upwork's available content corpus"; the terms page itself could not be fetched on 2026-11-04, so treat that exclusion as binding until re-read). Never a submission without his explicit confirmation of that specific proposal. If a submission's outcome is unclear, check submitted proposals and the Connects balance instead of resubmitting. (clm_up_005, clm_up_006, clm_up_007)

### Contact details and off-platform work

| Rule | Claims |
| --- | --- |
| Before a contract, sharing or requesting contact information or outside channels is circumvention: email, phone, address, Skype, Telegram, Slack, WeChat, WhatsApp, LinkedIn or other social handles, in a proposal or interview. Consequences range from restrictions and badge loss to permanent account loss. Asking to be paid outside Upwork is a violation even if no payment happens. | clm_up_008 |
| Allowed before a contract: your name, company name, and a link to a website you built. Exceptions for contact details: Enterprise plans; legal needs such as an NDA or background check; an email needed for system access to scope work (GitHub, analytics, cloud drives, e-signature, hosting). Communication still stays on Upwork until the contract starts. | clm_up_009 |
| Compliant line when a client asks: "I'll share my contact information once we have a contract in place." | clm_up_008 |
| Users who meet through Upwork must keep work and payments on Upwork for the first two years. The only compliant exit inside that window is the **Conversion Fee**, usually client-initiated and paid before any off-platform payment: 13.5% x the freelancer's hourly rate x 2,080 hours (highest rate with that client for hourly; profile rate for fixed). | clm_up_010 |
| Relationships that started off Upwork (Direct Contracts, Bring Your Own) are exempt. | clm_up_012 |
| The older "Opt-Out Fee" minimum and maximum are **unverified**; do not quote them. | clm_up_011 |

Freelance-legend's own policy is stricter than the allowance for "a link to a website you built": a link goes into a proposal only when the freelancer has approved it in his live `approved-proof.md` (in his user data directory; see the `freelance-legend` router) and the page it opens shows no contact details.

### Fees, Connects, and boosts

| Rule | Claims |
| --- | --- |
| Freelancer Service Fee is 0% to 15% per contract, shown at proposal or offer time, locked once sent, charged on all earnings including bonuses, and refunded on any amount refunded to the client. Read it from the apply screen; never assume it. the freelancer's 2026-11-04 apply page showed 10%, "fixed for the entire contract". The date the variable fee began is **unverified**. | clm_up_013, clm_up_014 |
| Gross rate for a target net: gross = net / (1 - fee). | clm_up_013 |
| Connects cost $0.15 each, sold in bundles; the number per proposal varies by job and can change while a post is live. Returned Connects are credits, not cash. | clm_up_015 |
| Connects come back if the client cancels before a contract or Upwork removes the post; not when the client picks someone else, the job expires, or the freelancer withdraws. | clm_up_016 |
| Boosted Proposals: top four bids get boosted slots; base Connects are charged immediately; the bid is charged at the end of the auction or on an eligible client interaction (open, shortlist, message, archive, decline, offer); no charge if outbid before any interaction. Auction closes after 7 days or first hire. A boost cannot be adjusted after submission. | clm_up_017 |
| Upwork runs placebo auctions on a small random share of posts (boost not charged, organic ranking). Upwork says boosting can raise hiring chances by up to 24%; treat that as Upwork's own claim. | clm_up_018 |
| Freelancer Plus includes 100 Connects a month, instant job alerts, bid insights, full Uma access, and 0% fee on Direct Contracts. Price is shown only in account settings; do not quote one. | clm_up_032 |

### Proposals

| Rule | Claims |
| --- | --- |
| Official guidance: say what you will do for the client, ask questions, suggest a next step in Upwork Messages or a video call, answer screening questions, add profile highlights (at least one portfolio highlight is required), proofread. Do not keep contacting an unresponsive client before a contract. | clm_up_027 |
| Cover letter, screening answers, highlights, and attachments can be edited for 6 hours after submitting or until the client views it, whichever comes first; afterwards only terms (rate or price, milestones, timeline) or a boost, until the client accepts, rejects, or offers. | clm_up_019 |
| Cover letter length: Upwork documents no limit. Third parties report 5,000 characters total and that clients see about the first 240 characters in the list. **Unverified**; use as a planning guide. | clm_up_026 |
| Specialized Profiles were removed 2026-05-28; their portfolio, history, and reviews merged into the main profile (titles, overviews, and skills did not). The main profile now surfaces the most relevant work per client automatically. | clm_up_020 |
| Scheduled rate increases: only on new hourly contracts with non-Enterprise clients, chosen in the proposal (frequency and percent). The client can accept, decline, or set their own; once agreed it is permanent and cannot be added later. | clm_up_021 |
| Uma is Upwork's AI assistant; some posts require an Uma video interview instead of a cover letter. Uma Recruiter invitations do not mean the client personally reviewed the freelancer. Upwork recommends disclosing generative AI use and respecting a client's ban on it. No rule banning AI-assisted proposals as such was found (**unverified**). | clm_up_024, clm_up_025 |
| Avoid duplicates: check existing invitations and proposals before drafting; an invitation gets an invitation reply, not a new proposal. A proposal status of "Accepted" means submitted and validated, not hired. The client must message first on a proposal (from Upwork's official skill; **unverified** elsewhere). | clm_gh_013, clm_gh_014 |
| Location: on US-only posts only US freelancers can apply; state and time-zone choices are preferences. Other location settings are preferences shown on the post, so a mismatch lowers odds rather than blocking. | clm_up_033 |

### Contracts and protection

| Rule | Claims |
| --- | --- |
| Hourly Payment Protection needs the Upwork Desktop App tracker, relevant screenshots, memos, fair activity, staying within the weekly limit, verified identity, a client with verified billing, and good standing. Manual, idle, over-limit, or memo-less time is excluded. Three days to respond to an hourly dispute. | clm_up_022 |
| Fixed-price protection applies only when the milestone was funded before work began, delivered through Submit Work for Payment, and matches the milestone description. Submitting starts a 14-day auto-payment countdown. Unfunded milestones cannot be recovered. | clm_up_023 |

### Reputation

| Rule | Claims |
| --- | --- |
| JSS is calculated daily over 6-, 12-, and 24-month windows, best shown; 90%+ excellent, below 79% hurts. Higher-earning contracts weigh more. No payment and no feedback is neutral; no payment with negative feedback can hurt. | clm_up_028 |
| Rising Talent, Top Rated, and Top Rated Plus thresholds are in the cited help pages; each badge awards 30 Connects; off-platform payment or repeated pre-contract off-platform contact loses badges for 6 months. | clm_up_029 |
| Project Catalog: up to 20 live projects (plus 20 in review), up to three tiers each, add-ons, up to five search tags, prices from $5 to $500,000; projects are reviewed by Upwork. | clm_up_030 |

### Scams and free work

| Rule | Claims |
| --- | --- |
| Upwork forbids clients requesting free work (unpaid trials, contests, spec work); test projects must be paid. | clm_cr_014 |
| Pushing to Telegram, WhatsApp, or an outside video call before a contract is a scam red flag and a terms violation; report it. Taking payment outside Upwork removes protection and is a common scam technique. | clm_cr_011, clm_cr_013 |
| Reported (single third-party source, **unverified**): fake-recruiter campaigns target developers with take-home repositories that run malware on opening or `npm run dev`. Treat as a precaution. | clm_cr_015 |
| FTC: task scams and fake checks (see the ledger for FTC figures); report at ReportFraud.ftc.gov and to the state attorney general. | clm_cr_007, clm_cr_009, clm_cr_029 |

## Direct outreach (US)

| Rule | Claims |
| --- | --- |
| CAN-SPAM covers B2B commercial email. It requires accurate headers, a non-deceptive subject, disclosure that the message is an ad, a valid physical postal address, and a working opt-out honored within 10 business days and kept working 30 days. | clm_cr_001, clm_cr_002, clm_cr_003 |
| LinkedIn prohibits untargeted or repetitive messages and promotional use of invitations to strangers; promotional messages may fall under CAN-SPAM. | clm_cr_005, clm_cr_006 |

## Other platforms

| Platform | Allowed intake | Prohibited | Freelancer fee | Fit for the freelancer | Claims |
| --- | --- | --- | --- | --- | --- |
| Hacker News "Who is hiring?" | Official Firebase API and the HN Algolia search API to find the monthly threads and read comments; at most daily, cached | Auto-posting or mass email from parsed threads; contact a poster only with the freelancer's interest, one tailored message | None | High for remote contract and startup leads; the freelancer can post in "Who wants to be hired?" himself | clm_pl_001, clm_pl_002, clm_pl_004 |
| HN "Freelancer? Seeking freelancer?" | Detect by query; do not assume it exists each month (none seen Sep to Nov 2026) | Same as above | None | Medium | clm_pl_003 |
| We Work Remotely | Public category RSS (for example full-stack programming), no more than hourly, respecting robots.txt | Account areas; crawling listing pages beyond the feed | None to applicants | Medium (mostly full-time; filter for contract and US or anywhere) | clm_pl_005 |
| LinkedIn | the freelancer's own job-alert emails; Service Page requests for proposal he pastes | Scraping, crawlers, extensions, bots for messaging, connecting, or auto-apply (User Agreement 8.2) | Free Service Page; Premium optional | High for finance plus full-stack consulting. Payment is arranged off LinkedIn, so use `contracts-scope` for an SOW and deposit | clm_pl_006, clm_pl_007, clm_pl_008 |
| Contra | Pasted opportunities and Contra emails | Crawlers and data mining; automated tools to get around outreach limits | 0% commission for freelancers (optional Pro plan); client fee **unverified** | High for project-based product, AI, and portfolio presence | clm_pl_009, clm_pl_010, clm_pl_011 |
| Freelancer.com | Email notifications and pasted listings only | Robots, scrapers, and automated access, **including its API without express written permission** | 10% (or $5 minimum) fixed, 10% hourly | Low to medium (price-competitive) | clm_pl_012, clm_pl_013 |
| Fiverr | Gig copy written offline; Brief text the freelancer pastes | Treat automation as prohibited (clause **unverified**); no off-platform payment | 20% seller fee (third-party consensus, **unverified** officially); gross up package prices | Medium for productized gigs (ROI calculator, financial model, Next.js and Supabase MVP) | clm_pl_030, clm_pl_031 |
| Toptal | Application prep; client briefs he receives | Page scrapers, spiders, robots, deep links | None to talent | High but gated: multi-stage screening (language, skills test, live screen, test project) over weeks | clm_pl_022, clm_pl_023, clm_pl_024 |
| Arc.dev | Pasted matches and emails | Scripts, robots, scraping, repeated monitoring; soliciting off-platform payment. **Never discuss the freelancer's compensation with an Arc client** (contract forbids it) | Developer fee **unverified** | High for remote contract dev roles | clm_pl_020, clm_pl_021 |
| Wellfound | Email notifications and pasted listings | Harvesting or scraping; automated access beyond human load | None stated; do not claim | Medium (startups, mostly full-time; filter contract or fractional) | clm_pl_018, clm_pl_019 |
| Braintrust | Pasted listings and emails | Assume no automation (terms not readable) | 0% talent fee (seen in official FAQ excerpts); client fee unsettled | High for senior contract engineering and AI | clm_pl_025 |
| Gun.io | Pasted matches | Assume no automation; stay on platform with its clients | Platform fee is included in the rate the client sees | Medium to high | clm_pl_026 |
| PeoplePerHour | Notification emails and pasted projects | Treat automation as prohibited; all payments including follow-on work stay on PPH | 20% up to $350 lifetime per buyer, 7.5% to $7,000, 3.5% above (excluding VAT) | Low to medium (UK-centric) | clm_pl_027, clm_pl_028, clm_pl_029 |
| Indeed | Indeed alert emails and pasted listings only | Any bots, scrapers, or AI or agentic AI accessing or submitting content; automating Indeed Apply. Never open Indeed pages for the freelancer | None | Low to medium (mostly W-2) | clm_pl_015, clm_pl_016 |
| Dice | Alert emails and pasted listings | Unapproved spiders, robots, or intelligent agents navigating or storing; data mining | None | Medium for US contract roles | clm_pl_017 |
| Malt, Guru | Pasted listings only | Assume automation prohibited (terms not readable) | **Unverified**: say "check in account" | Low (Malt is Europe-focused); low to medium (Guru) | clm_pl_032, clm_pl_033 |

**Off-platform payment.** On escrow marketplaces (Upwork, PeoplePerHour, Arc, Fiverr, Freelancer.com) never propose moving payment off-platform, and flag a client who asks as a terms and scam risk. On LinkedIn Service Pages off-platform payment is the normal model, so require a written SOW and a deposit. (clm_up_008, clm_pl_008, clm_pl_020, clm_pl_028)

**Outreach on platforms.** No bulk or automated messaging on Contra or LinkedIn. Draft one message at a time for the freelancer to send. (clm_pl_006, clm_pl_011)
