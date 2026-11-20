# freelance-legend: research decision report (draft, 2026-11-04)

## Purpose

This report records the evidence behind the `freelance-legend` plugin: skills for Upwork and other freelance proposals and cover letters, compliant job scanning, job and scam vetting, pricing, client communications, profile work, a portfolio website, contracts, a pipeline tracker and outbound prospecting. It sets out what the plugin may automate, what it must refuse, and which platform facts it may state as fact. Platform rules change often, so every rule here is dated 2026-11-04.

## Method

- **Arms.** Five research arms ran in parallel:
  - `upwork`: the Upwork help center and press material.
  - `platforms`: terms and fees for HN, WWR, LinkedIn, Indeed, Dice, Contra, Freelancer.com, Fiverr, Toptal, Arc, Wellfound, Braintrust, Gun.io, PeoplePerHour, Malt and Guru.
  - `craft`: CAN-SPAM, LinkedIn messaging policy, FTC scam guidance, and Upwork disputes and feedback.
  - `portfolio`: Next.js docs, schema.org, Google structured data, and portfolio template prior art.
  - `tooling`: GitHub prior art for Upwork and freelance agent tooling.
- **Manual mode.** The research-first-creator local gate tooling is not configured in this repository. This ledger was assembled and checked by hand plus a python3 validation script. No `verified_claims.json` exists and no automated PASS is claimed.
- **Ledger re-check rule** (applied after the arms finished):
  - A non-executable claim stays `supported` only if it cites two distinct organizations, or a primary source rated A/B (official docs, terms, official blog or the repository itself) for a rule or fact that the publisher states about itself.
  - A high-risk supported claim must also carry a counter-search whose URLs are registered in `sources/sources.jsonl`. 108 counter-search URLs were added as `src_cs_*` entries. They are typed `official_docs` (rated B) or `third_party_article` (rated D), and many were seen only as search results.
  - The re-check downgraded 7 arm-supported claims to `unresolved`: one security claim with only one third-party source, and six descriptions of C/D-rated community repositories (see Unresolved).
- **Deduplication.** Sources were deduplicated by URL, treating Upwork help-center article IDs as one key, so 10 duplicate source IDs were merged and claim `source_ids` rewritten. The arms flagged `src_pl_030` as an unused placeholder, and it was dropped.
- **Tool failures reported by the arms:**
  - HTML pages on support.upwork.com, and the pages under upwork.com/legal, /ai/mcp and /resources, returned HTTP 403. Help articles were read through the public Zendesk JSON API instead. The User Agreement and the API and MCP Terms of Use were not read.
  - The craft and portfolio arms could reach Upwork pages only through search-index excerpts.
  - Fiverr, Guru, Malt, the WWR terms and the Toptal Talent Agreement returned 403. The Braintrust terms returned 404. The Freelancer.com developer docs returned 404.
  - The gh CLI authentication failed and per-repo REST calls were refused. SHAs come from shallow, blob-less clones in which no code was executed.
  - A retry with a browser user-agent was denied by the permission classifier, and no further retries were made.
- **Provenance of the prior-art columns.** Repo SHAs, paths, licenses and star counts in the Prior art table come from the arms' repository records and the `sources.jsonl` titles. They are metadata, not ledger claims.

Counts: 238 sources and 143 claims (109 supported, 34 unresolved, 0 refuted).

## Platform compliance matrix

| Platform | Machine intake allowed | Prohibited | Freelancer fee | Fit | Claims |
| --- | --- | --- | --- | --- | --- |
| Upwork | Official Upwork MCP server or the Claude connector (human-confirmed), Freelancer Plus instant alerts, saved searches, Job Digest, Recommended Jobs; text the user pastes | Scrapers, extensions, auto-refresh, page monitors, RPA, user scripts, reusing browser cookies or tokens, background polling, RSS polling; contact info before a contract | 0-15% per contract, shown at apply time and locked | High | clm_up_001, clm_up_002, clm_up_003, clm_up_005, clm_up_008, clm_up_013, clm_up_031, clm_gh_001 |
| Hacker News | Official Firebase API and the Algolia search API, read-only | No auto-posting; email posters only if personally interested | None | High for contract leads | clm_pl_001, clm_pl_002, clm_pl_004 |
| We Work Remotely | Public category RSS feeds (ttl 60), following robots.txt | Account and admin paths | None stated | Medium | clm_pl_005 |
| LinkedIn | The user's own alert emails; Service Page proposal requests the user pastes | Scraping, bots, plugins, automated messaging or liking; untargeted or repetitive messages | Service Page requests are free; payment happens off LinkedIn | High (Service Page) | clm_pl_006, clm_pl_007, clm_pl_008, clm_cr_005, clm_cr_006 |
| Indeed | Alert emails and pasted listings only | Any automated system, explicitly including agentic AI; automating Indeed Apply | None stated | Low-medium | clm_pl_015, clm_pl_016 |
| Dice | Alert emails and pasted listings | Robots, spiders, intelligent agents, data-mining | None stated | Medium (US contract) | clm_pl_017 |
| Contra | Pasted opportunities and notification emails | Crawlers other than Contra's own agents; dodging outreach rate limits | 0% commission; Pro is $29/mo | High | clm_pl_009, clm_pl_011 |
| Freelancer.com | Notification emails and pasted listings | Automated access, including the API, without written permission | 10% or $5 minimum (fixed price); 10% (hourly) | Low-medium | clm_pl_012, clm_pl_013 |
| Fiverr | Gig copy the user writes; buyer briefs the user pastes | Treat all automation as prohibited | 20% seller fee | Medium (productized gigs) | clm_pl_030 |
| Toptal | Application prep only | Scrapers, spiders, deep links | None charged to talent | High, but screened (about 3% pass) | clm_pl_022, clm_pl_023, clm_pl_024 |
| Arc | Pasted matches | Scripts, scraping, repeated monitoring; off-platform payments; telling clients your compensation | Not verified | High | clm_pl_020 |
| Wellfound | Notification emails and pasted listings | Harvesting or scraping; reusing content commercially | Not stated | Medium (startups) | clm_pl_018, clm_pl_019 |
| Braintrust | Pasted listings | Assume no automation | 0% talent fee | High (senior contract work) | clm_pl_025 |
| Gun.io | Pasted matches | Assume no automation | Fee included in the profile price | Medium-high | clm_pl_026 |
| PeoplePerHour | Notification emails and pasted projects | All payments, including follow-on work, must stay on PPH | 20% / 7.5% / 3.5%, tiered by lifetime billing per buyer | Low-medium | clm_pl_027, clm_pl_028 |

Malt and Guru fees and terms are unverified and listed under Unresolved.

## Upwork mechanics (dated 2026-11-04)

| Mechanic | Rule | Claims |
| --- | --- | --- |
| Automation | Any script, extension or service that sends requests or collects data automatically is a bot. There are no productivity-tool exceptions, and an API key does not permit scraping or spam. | clm_up_001, clm_up_002, clm_up_003, clm_gh_004 |
| Official MCP | Launched 2026-08-10 and free to use. Proposals are drafted, then explicitly confirmed by the user. Project Catalog cannot be managed through MCP. | clm_up_005, clm_gh_001, clm_gh_008 |
| MCP rate limits | Per account, in five categories, resetting at 00:00 UTC. Search 15/150/750 per minute/hour/day; writes 20/60/150. Limits may change. | clm_up_006, clm_gh_007 |
| Claude connector | Produces drafts only. Offers, milestone funding and approval, and weekly hour limits are handled on upwork.com. | clm_up_007 |
| API key | Personal or internal use only. Requires $25k lifetime earnings and/or spend, JSS 90%+, and staying under 40k requests a day. | clm_up_004 |
| Contact before a contract | Banned: email, phone, address, messaging IDs, social handles and outside meeting links. Exceptions: Enterprise plans, legal needs, and system access needed to scope work. Your name, company name and website links are allowed. | clm_up_008, clm_up_009, clm_gh_010 |
| Off-platform within 2 years | Allowed only through the Conversion Fee (13.5% x rate x 2,080 hours), usually started by the client. | clm_up_010, clm_up_012 |
| Service fee | 0-15% per contract, locked once sent, and charged on bonuses too. Direct Contracts are 0% with Freelancer Plus. | clm_up_013 |
| Connects | $0.15 each. The number required varies by job. Connects are returned only when the client cancels before hiring or Upwork removes the post. Withdrawing never returns them. | clm_up_015, clm_up_016, clm_gh_009 |
| Boosts | The top 4 bidders get a Boosted tag. The bid is charged on client interaction or when the auction closes (7 days or first hire). Placebo auctions exist. Upwork claims "up to 24%" more hires. | clm_up_017, clm_up_018 |
| Editing a proposal | Content can be edited within 6 hours or until the client views it. After that, only terms can change. | clm_up_019 |
| Proposal guidance | State what you will do, ask questions, suggest a next step in Upwork Messages, answer every screening question, include at least one portfolio highlight, and proofread. | clm_up_027 |
| AI and Uma | Upwork recommends disclosing generative AI use. Some posts require an Uma video interview. Uma Recruiter invites do not mean the client reviewed you personally. | clm_up_024 |
| Specialized Profiles | Removed 2026-05-28. The main profile now shows each client the most relevant work first. | clm_up_020 |
| Scheduled rate increase | New hourly, non-Enterprise contracts only. Must be set in the proposal and is permanent once agreed. | clm_up_021 |
| Hourly Protection | Requires the Desktop App tracker, memos, activity, and staying within the weekly limit. You have 3 days to answer a dispute. | clm_up_022 |
| Fixed-price Protection | The milestone must be funded first, and work delivered through Submit Work. Funds release automatically after 14 days. | clm_up_023, clm_cr_017 |
| Disputes | Workroom first, then free mediation, then optional binding arbitration if escrow was ever funded. | clm_cr_018 |
| JSS and badges | Best score of the 6/12/24-month windows. Badge thresholds are known, and badges are lost for 6 months for off-platform behavior. | clm_up_028, clm_up_029 |
| Project Catalog | Up to 20 live projects, 3 tiers each, 5 tags, priced $5-$500k. | clm_up_030 |
| Alerts | Freelancer Plus instant alerts, saved searches, Job Digest and Recommended Jobs. RSS was turned off after 2024-08-20. | clm_up_031, clm_gh_005, clm_gh_006 |
| Freelancer Plus | 100 Connects a month, alerts, bid insights and full Uma. The help center does not state the price. | clm_up_032 |
| Location | US-only posts are restricted to US freelancers. Other location settings are preferences. | clm_up_033 |
| Scams | Unpaid tests are not allowed (paid tests are). Paying off-platform voids protection. Being pushed to Telegram or WhatsApp is a red flag. | clm_cr_011, clm_cr_013, clm_cr_014 |

## Prior art

| Requirement | Finalist repo@sha:path | Grade | Gap | License decision | Original-design choice |
| --- | --- | --- | --- | --- | --- |
| Live Upwork connection and proposal submit flow | upwork/upwork-agent-plugin@7908a7e:skills/write-proposal/SKILL.md | A | Upwork-only; no vetting rubric, other platforms, pricing or portfolio (clm_gh_001, clm_gh_013) | Apache-2.0; no code or text vendored | Our skills call the official MCP for live data. Submit is gated by a preview and explicit approval (clm_gh_008, clm_up_005) |
| Proposal method and job qualifier | abullaisi/upwork-skills@9d82de6:upwork-proposal-writer/SKILL.md | B | Its method details and statistics rest on a single source (see Unresolved). It encodes the no-contact rule (clm_gh_010) | MIT; ideas only | Proposal structure built from Upwork's own guidance plus a contact-info lint (clm_up_027, clm_up_008) |
| Pipeline state and evidence confidence | career-ops-hq/career-ops@d430f83:templates/states.yml | B | Built for full-time job search, not freelancing (clm_gh_020, clm_gh_021) | MIT; ideas only | Freelance-specific canonical state file, with evidence confidence kept separate from the score |
| Deterministic job scoring and Connects ROI | waseemnasir2k26/upwork-mcp-toolkit@67d1850:src/upwork_kit/scoring.py | B (arm) | No adoption; method claims single-source (see Unresolved). Uses the $0.15 Connects price (clm_gh_009) | MIT; ideas only | Original rubric. Thresholds live in user config and are labeled as the user's taste |
| Client quality score | Nadarisgetae/Upwork-Asisstance-Plugin@4aff5b6:skills/client-analysis/client-quality-score/SKILL.md | C | Logic split across many tiny skills; single-source | No LICENSE file; reference only | Calibration anchors re-scored whenever weights change (own implementation) |
| Proposal style lint | Adithya-13/upwork-proposal-skill@00cdc3d:skills/upwork-proposal-writer/SKILL.md | C | Gimmicky Unicode bold; single-source | MIT; ideas only | Optional style lint, never a hard gate |
| Community API MCP | furkankoykiran/upwork-mcp@9ed7b44:src/client/rate-limiter.ts | C | Compliant only with an approved API key (clm_gh_023) | MIT; reference only | Prefer the official MCP |
| Scrapers (anti-pattern) | roperi/UpworkScraper@6924d06:upwork_scraper/auth.py; richardadonnell/Upwork-Job-Scraper@bc54564:README.md | D | The exact automation patterns Upwork bans (clm_gh_011, clm_gh_012) | Avoid | Scanner refuses to build these |
| Invoices and SOW | VladSez/easy-invoice-pdf@454240c:src/app/schema/index.ts; mazer-dev/pejota@72226f1:app/Enums/InvoiceStatusEnum.php | B / C | Code is AGPL or unlicensed; rate calculator prior art is thin (clm_gh_024) | Reference only | Original templates; reuse field ideas such as tax rate and status set |
| Portfolio reference architecture | vercel/examples@de86723:solutions/blog/app/blog/[slug]/page.tsx | Strong | Its JSON-LD skips the docs-recommended escaping (clm_pf_001, clm_pf_006) | Used as a feature checklist only | Write from scratch, with escaped JSON-LD |
| Case studies and gated NDA pages | once-ui-system/magic-portfolio@bee2f1b:src/app/work/[slug]/page.tsx | Strong | CC BY-NC license (clm_pf_014, clm_pf_015, clm_pf_016) | Ideas only; no code | Independent password-gate implementation; gated pages set to noindex |
| JSON-LD @graph | mldangelo/personal-site@cae7b4c:src/lib/schema.ts | Match | Exposes email (clm_pf_019, clm_pf_020) | MIT; ideas only | Stable #person @id with contact fields stripped in the proposal-safe build |
| Single content config and OG images | magicuidesign/portfolio@5ef12e4:src/app/opengraph-image.tsx | Match (stale) | Stale (clm_pf_017, clm_pf_022) | MIT; ideas only | One typed config file drives pages, metadata, OG images and JSON-LD |
| Metadata and RSS patterns | timlrx/tailwind-nextjs-starter-blog@b45bef6:app/layout.tsx | Match (stale) | Blog-first; stale (clm_pf_018, clm_pf_022) | MIT; ideas only | Native Metadata API (clm_pf_003) |
| Minimal MDX routing | leerob/next-mdx-blog@c9893c6:mdx-components.tsx | Adjacent | Unlicensed (clm_pf_021) | No reuse | `@next/mdx` with a separate frontmatter parser (clm_pf_005) |
| Astro alternative | RyanFitzgerald/devportfolio@852d650:src/components/Projects.astro | Adjacent (stale) | Different framework; stale (clm_pf_022) | Mention only | Not used |

## Design decisions

1. Live Upwork access goes only through the official Upwork MCP server or the Claude connector. Otherwise the user pastes the job post and client panel. (clm_up_005, clm_up_007, clm_gh_001, clm_up_031)
2. Every skill refuses to scrape, poll, run browser automation on a logged-in session, reuse cookies or tokens, build extensions, or poll RSS against Upwork, and refuses to build such tools when asked. (clm_up_001, clm_up_002, clm_up_003, clm_gh_011, clm_gh_012)
3. Requests are budgeted under the MCP per-category caps, never retried in a loop, and the limits are re-checked at runtime because Upwork can change them. (clm_up_006, clm_gh_007)
4. Submission is always human-gated: draft, then preview (letter, answers, bid, Connects, boost), then separate approvals. Unattended runs never submit or message. If an outcome is unclear, check pending proposals and the Connects balance instead of resubmitting. (clm_gh_008, clm_gh_013, clm_gh_020)
5. A contact-info lint blocks email, phone, address, messaging and social handles, and meeting links in proposals and pre-contract messages. The user's name, company and portfolio site links are allowed. (clm_up_008, clm_up_009, clm_gh_010)
6. When a client asks to move chat or payment off-platform, the plugin drafts a polite decline, flags the request as a scam risk, and names the Conversion Fee as the only compliant route within two years. (clm_up_008, clm_up_010, clm_up_012, clm_cr_011, clm_cr_013)
7. Proposal structure follows Upwork's guidance: the client outcome, focused questions, a next step in Upwork Messages, every screening question answered, at least one portfolio highlight, and a proofread. The letter is finalized before sending because the edit window is short. (clm_up_027, clm_up_019)
8. Pricing reads the fee from the apply screen and grosses up: gross = net / (1 - fee). The fee also applies to bonuses. Each platform's fee lives in a versioned config with source and date. (clm_up_013, clm_pl_012, clm_pl_027, clm_pl_030)
9. Bid economics: cost = Connects x $0.15 + boost. Boost only strong-fit, high-value jobs. Withdrawing never returns Connects. (clm_up_015, clm_up_016, clm_up_017, clm_up_018)
10. Vetting hard-stops on: payment or contact off-platform, requests for free work, fees or deposits, check or overpayment schemes, task-scam patterns, and requests for off-platform contact before a contract. Original design choice, not a platform rule: missing client data gives a HOLD verdict, never a pass. (clm_cr_008, clm_cr_009, clm_cr_010, clm_cr_011, clm_cr_014, clm_up_008)
11. Contracts: never start an unfunded milestone; deliver through Submit Work; keep tracker memos on hourly work; route scope growth into a new milestone. (clm_up_022, clm_up_023, clm_cr_017, clm_cr_018)
12. Hourly proposals may offer a scheduled rate increase, because it cannot be added once the contract starts. (clm_up_021)
13. Profile: one broad, keyword-rich main profile with varied portfolio items. Old Specialized Profile advice is out of date. Project Catalog listings are edited by the user in the Upwork UI. (clm_up_020, clm_up_030, clm_up_005)
14. Reputation: track JSS and badge thresholds, and warn that off-platform behavior costs badges for 6 months. (clm_up_028, clm_up_029)
15. AI disclosure: the plugin drafts, the human edits and submits, disclosure is recommended, and the plugin prepares talking points for Uma interviews. Uma Recruiter invites score lower than personal invites. (clm_up_024)
16. Other platforms are read automatically only through the HN Firebase or Algolia APIs and WWR RSS. Everything else comes from forwarded alert emails or pasted text. (clm_pl_001, clm_pl_002, clm_pl_005, clm_pl_006, clm_pl_013, clm_pl_015, clm_pl_017, clm_pl_018, clm_pl_020, clm_pl_022, clm_pl_011)
17. Arc rule: never discuss the freelancer's compensation with an Arc client. (clm_pl_020)
18. Cold email output carries a CAN-SPAM checklist: true headers, an honest subject, a solicitation disclosure, a postal address, an opt-out honored within 10 business days, and a warning that penalties apply per email and B2B is not exempt. (clm_cr_001, clm_cr_002, clm_cr_003, clm_cr_004)
19. LinkedIn outreach is one-to-one and relevant, with no pitch in invites to strangers and no sending after a decline. (clm_cr_005, clm_cr_006, clm_pl_006)
20. Fraud reporting guidance: contact the payment provider, ReportFraud.ftc.gov, and the state attorney general. Never forward money from a check. (clm_cr_029, clm_cr_009)
21. Portfolio site: Next.js App Router, MDX case studies with a separate frontmatter parser, the native Metadata API with shared OG spreads, 1200x630 OG images, and escaped JSON-LD with one Person @id. Do not use the ProfessionalService type, and mark up only visible content. (clm_pf_001, clm_pf_002, clm_pf_003, clm_pf_004, clm_pf_005, clm_pf_007, clm_pf_008, clm_pf_009, clm_pf_010)
22. A proposal-safe build mode strips every contact channel, backed by a pre-publish scan, because stock templates ship contact pages. (clm_pf_020, clm_pf_019, clm_up_008, clm_up_009)
23. Write all code and templates from scratch. Code under CC BY-NC, AGPL or no license is idea-only. (clm_pf_016, clm_pf_021, clm_gh_024)
24. Do not hardcode volatile figures (the Freelancer Plus price, Contra client fees, Braintrust client fees). Point users to the live screen. (clm_up_032, clm_pl_009, clm_pl_025)

## Unresolved

- clm_up_011: Opt-Out Fee rename and old $1k-$50k bounds. Only forum and tracker evidence exists.
- clm_up_014: Effective date of the variable 0-15% fee. Third-party sources conflict.
- clm_up_025: Absence of an Upwork rule against AI-assisted proposals. The User Agreement returned 403.
- clm_up_026: 5,000-character cover-letter limit and a roughly 240-character preview. Third-party only.
- clm_pl_010: Contra client fee ($19 vs $29). Sources conflict.
- clm_pl_014: Freelancer.com $20 minimum balance to bid. Unconfirmed.
- clm_pl_021: Arc charges developers no commission. Third-party only.
- clm_pl_029: PeoplePerHour anti-scraping clause. Not found in the terms text.
- clm_pl_031: Fiverr anti-scraping clause. Primary page blocked.
- clm_pl_032: Malt commission tiers. Help pages conflict and returned 403.
- clm_pl_033: Guru fee tiers. Third-party only.
- clm_cr_012: Upwork contact-info exceptions as the craft arm read them (search excerpts only). The same core rule is supported elsewhere as clm_up_008 and clm_up_009.
- clm_cr_015: Fake-interview malware repos aimed at developers. **Downgraded by the ledger re-check**: only one third-party source (The Register) was read. Kept as a precaution in design-notes.
- clm_cr_016: Account renting is prohibited. Upwork announcement seen only in an excerpt.
- clm_cr_019: Arbitration fee of $337.50 per side. Third-party only.
- clm_cr_020: Window for clients to dispute hourly time. Excerpts only.
- clm_cr_021: 14-day double-blind feedback window. Excerpts only.
- clm_cr_022: Feedback-manipulation prohibition. Excerpts and moderator posts only.
- clm_cr_023: Changing future milestones on an active contract. Excerpts only.
- clm_cr_024: Organic ranking factors for proposals. Excerpts conflict on 3 vs 4 boosted slots.
- clm_cr_025: Roughly 200-character proposal preview. Third-party heuristic.
- clm_cr_026: 600-1,000 character length recommendation. Single third-party source.
- clm_cr_027: Speed-to-apply statistics. Vendor claims.
- clm_cr_028: A cadence of 2-3 follow-ups. Opinion only.
- clm_pf_011: Contact-info rule as the portfolio arm read it (403). The same rule is supported as clm_up_008.
- clm_pf_012: Whether a portfolio link that exposes contact info is allowed. Upwork moderators are split.
- clm_gh_014: The client must message first; "Accepted" means submitted, not hired. Only the official repo says so.
- clm_gh_015: abullaisi proposal method. **Downgraded**: single C-rated source.
- clm_gh_016: abullaisi qualifier (HOLD verdict, instant skips). **Downgraded**: single C-rated source.
- clm_gh_017: upwork-mcp-toolkit scoring weights. **Downgraded**: single C-rated source.
- clm_gh_018: upwork-mcp-toolkit red-flag regex and Connects EV prior. **Downgraded**: single C-rated source.
- clm_gh_019: Nadarisgetae weighted client score. **Downgraded**: single D-rated source.
- clm_gh_022: Adithya-13 secret-word check and banned-word list. **Downgraded**: single C-rated source.
- clm_gh_025: Claims of 9x hires with a portfolio, 17% boost visibility, and 10-20 Connects to win a boost. Unverified.

## Refuted

None. No claim was contradicted by a primary source in this run.
